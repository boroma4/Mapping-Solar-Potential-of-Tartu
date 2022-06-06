import json
import logging
import os
import xml.etree.ElementTree as ET

from lib.citygml.building import Building
from lib.util.constants import *
from lib.pipeline import Pipeline, UPDATED_PREFIX
from lib.solar_potential.pvgis_api import PvgisRequestBuilder, make_empty_response
from lib.util.decorators import timed
from lib.util.file_size import get_file_size_mb


class SolarPotentialPipeline(Pipeline):
    def run(self, level, pv_efficiency, pv_loss, roof_coverage, optimize_2d, output_format):
        logging.info("Running Solar Potential pipeline")
        self.pv_efficiency = pv_efficiency
        self.pv_loss = pv_loss
        self.roof_coverage = roof_coverage
        self.optimize_2d = optimize_2d
        self.output_format = output_format

        self.process_files(level, self.process_city_gml_file)

    def process_city_gml_file(self, tree, path_util, filename):
        self.path_util = path_util
        buildings = tree.getroot().findall(f"{CORE}cityObjectMember")
        attribute_map = self.__get_building_attributes(buildings)
        attribute_map = self.__add_solar_potential_to_attribute_map(attribute_map)
        pv_output_map = self.__calculate_city_solar_stats(attribute_map)
        pv_output_map["file"] = filename

        original_file_path = path_util.get_path_gml(filename)
        output_dir_path = original_file_path.removesuffix(".gml") + "-output"
        processed_file_path = os.path.join(output_dir_path, f"{UPDATED_PREFIX}{filename}")

        if not os.path.exists(output_dir_path):
            os.mkdir(output_dir_path)

        self.__write_solar_output_to_tree(buildings, attribute_map)
        tree.write(processed_file_path)

        logging.info("Wrtiting results to JSON files")
        self.__write_city_attributes_json(attribute_map, output_dir_path)
        self.__write_city_pv_json(pv_output_map, output_dir_path)

        # Converting CityGML to visualizable format
        self.__convert_citygml_to_output_format(processed_file_path, output_dir_path)

        logging.info(f'Output files can be located at {output_dir_path}')

    @timed("Building analysis")
    def __get_building_attributes(self, buildings):
        count_total = len(buildings)
        count_processed = 0
        count_no_roofs = 0
        count_roofs = 0
        attribute_map = {}

        logging.info("Analyzing CityGML file")

        for xml_building in buildings:
            building_id = self.extract_integer_id(xml_building[0].attrib[ID])
            building = Building(building_id, xml_building)

            if self.optimize_2d:
                building.optimize_for_2d_map()
                z_min = 0
            else:
                z_min = building.get_z_min()

            attribute_map[building_id] = attribute_map.get(building_id, {})
            attribute_map[building_id]["roofs"] = []

            for surface in building.get_surfaces():
                # A surface with area less than 2 m2 is not really suitable for solar panels
                if not surface.is_roof(z_min) or surface.area < 2:
                    continue

                count_roofs += 1
                roof_attribs = {"area": surface.area, "azimuth": surface.azimuth, "tilt": surface.tilt, "orientation": surface.orientation}

                # handling duplicated points
                if roof_attribs not in attribute_map[building_id]["roofs"]:
                    attribute_map[building_id]["roofs"].append(roof_attribs)

            if "roofs" not in attribute_map[building_id]:
                count_no_roofs += 1
                attribute_map[building_id]["roofs"] = [{"area": 0, "azimuth": 0, "tilt": 0}]

            building_attributes = attribute_map[building_id]
            roofs = building_attributes["roofs"]

            total_roof_area = round(sum([roof["area"] for roof in roofs]), 3)
            north_roof_area = round(sum([roof["area"] for roof in roofs if roof["orientation"] == NORTH]), 3)
            south_roof_area = round(sum([roof["area"] for roof in roofs if roof["orientation"] == SOUTH]), 3)
            west_roof_area = round(sum([roof["area"] for roof in roofs if roof["orientation"] == WEST]), 3)
            east_roof_area = round(sum([roof["area"] for roof in roofs if roof["orientation"] == EAST]), 3)
            flat_roof_area = round(sum([roof["area"] for roof in roofs if roof["orientation"] == NONE]), 3)

            lat, lon = building.get_approx_lat_lon()

            building_attributes["total_roof_area"] = round(total_roof_area, 2)
            building_attributes["lat"] = lat
            building_attributes["lon"] = lon
            self.__update_tree(xml_building, [
                ["area", "doubleAttribute", total_roof_area],
                ["north-area", "doubleAttribute", north_roof_area],
                ["south-area", "doubleAttribute", south_roof_area],
                ["west-area", "doubleAttribute", west_roof_area],
                ["east-area", "doubleAttribute", east_roof_area], 
                ["flat-area", "doubleAttribute", flat_roof_area], 
                ["etak_id", "stringAttribute", building_id]])

            count_processed += 1
            if count_processed % 5000 == 0:
                logging.info(f"Processed {count_processed}/{count_total} buildings")

        logging.info(
            f"Roofs not detected for {count_no_roofs}/{count_total} buildings")
        logging.info(f"{count_roofs} roof surfaces detected")

        return attribute_map

    @timed("Estimating solar potential through PVGIS requests")
    def __add_solar_potential_to_attribute_map(self, attribute_map):
        logging.info("Obtaining solar potential from PVGIS API")
        payload_map = {}

        # For each building an array of it's roof surfaces is processed
        for building_id, data in attribute_map.items():
            payload_map[building_id] = []
            for roof in data["roofs"]:
                roof_area = roof["area"]
                orientation = roof["orientation"]
                lat = data["lat"]
                lon = data["lon"]

                # area of the roof that can be covered
                usable_roof_area = roof_area * self.roof_coverage
                # peak power of the PV array installed
                peak_power_kpw = usable_roof_area * self.pv_efficiency

                request_builder = PvgisRequestBuilder() \
                    .set_location(lon, lat) \
                    .set_peak_power_kwp(peak_power_kpw) \
                    .set_mounting_place("building") \
                    .set_loss(self.pv_loss) \
                    .set_angle(roof["tilt"]) \
                    .set_azimuth(roof["azimuth"])

                # Uses best possible angles becacuse it should be easy to adjust those on a flat-ish roof
                if roof["tilt"] <= FLAT_SURFACE_MAX_TILT:
                    request_builder.optimize_angles()

                request_data = [orientation, request_builder.get_payload()]
                payload_map[building_id].append(request_data)

        logging.info("Storing requests data to be processed by Node.js script")

        tmp_dir_path = self.path_util.get_tmp_dir_path()
        requests_json_path = tmp_dir_path + "/requests.json"

        with open(requests_json_path, 'w') as fp:
            json.dump(payload_map, fp)
            logging.info(f"File created: {requests_json_path}")

        # calls the Node.js script which saves results to a new json file
        self.__send_pvgis_api_requests()

        responses_json_path = tmp_dir_path + "/responses.json"
        json_file_size_mb = get_file_size_mb(responses_json_path)
        logging.info(f"Responses JSON is {json_file_size_mb} MB")

        with open(responses_json_path, 'r') as fp:
            pv_data = json.loads(fp.read())

        # Processing API results for each roof of each building
        for building_id in attribute_map.keys():
            # If building area is 0, request to the API will return an error instead
            # of data and it won't be added to responses json
            if building_id not in pv_data:
                pv_data[building_id] = [make_empty_response()]

            for i in range(len(pv_data[building_id])):
                roof_pv_data = pv_data[building_id][i]
                roof_pv_data["totals"]["fixed"]["E_m_exact"] = []

                for month in range(12):
                    monthly_power = roof_pv_data["monthly"]["fixed"][month]["E_m"] or 0
                    roof_pv_data["totals"]["fixed"]["E_m_exact"].append(monthly_power)

            # shrink the dict a bit
            roofs_pv_list = [data["totals"]["fixed"] | {"orientation": data["orientation"]} for data in pv_data[building_id]]

            # In case yearly energy is None
            for roof_pv in roofs_pv_list:
                roof_pv["E_y"] = roof_pv["E_y"] or 0

            attribute_map[building_id] = {"building": attribute_map[building_id], "roofs_pv_list": roofs_pv_list}

        return attribute_map

    # Calculates estimated monthly and yearly energy production for the whole city

    def __calculate_city_solar_stats(self, attribute_map):
        output = {}
        total_yearly = 0
        total_monthly = [0] * 12

        for building_data in attribute_map.values():
            roof_pv_data_list = building_data["roofs_pv_list"]
            total_yearly += round(sum([el["E_y"] for el in roof_pv_data_list]), 3)
            for month in range(12):
                total_monthly[month] += round(sum([el["E_m_exact"][month] for el in roof_pv_data_list]), 3)

        output["total_yearly_energy_kwh"] = total_yearly
        output["total_monthly_energy_kwh_list"] = total_monthly
        return output

    @timed("Updating the XML tree with solar data")
    def __write_solar_output_to_tree(self, buildings, attribute_map):
        for xml_building in buildings:
            id = self.extract_integer_id(xml_building[0].attrib[ID])
            roofs_pv = attribute_map[id]["roofs_pv_list"]
            total_yearly_power = round(sum([roof_pv["E_y"] for roof_pv in roofs_pv]), 3)
            north_yearly_power = round(sum([roof_pv["E_y"] for roof_pv in roofs_pv if roof_pv["orientation"] == NORTH]), 3)
            south_yearly_power = round(sum([roof_pv["E_y"] for roof_pv in roofs_pv if roof_pv["orientation"] == SOUTH]), 3)
            west_yearly_power = round(sum([roof_pv["E_y"] for roof_pv in roofs_pv if roof_pv["orientation"] == WEST]), 3)
            east_yearly_power = round(sum([roof_pv["E_y"] for roof_pv in roofs_pv if roof_pv["orientation"] == EAST]), 3)
            optimized_yearly_power = round(sum([roof_pv["E_y"] for roof_pv in roofs_pv if roof_pv["orientation"] == NONE]), 3)


            self.__update_tree(xml_building, [
                ["power", "doubleAttribute", total_yearly_power],
                ["north-power", "doubleAttribute", north_yearly_power],
                ["south-power", "doubleAttribute", south_yearly_power],
                ["west-power", "doubleAttribute", west_yearly_power],
                ["east-power", "doubleAttribute", east_yearly_power],
                ["optimized-power", "doubleAttribute", optimized_yearly_power],
            ])

    def __send_pvgis_api_requests(self):
        logging.info("Running batch-pvgis-requests.mjs")
        tmp_dir_path = self.path_util.get_tmp_dir_path()
        js_script_path = self.path_util.get_js_script('batch-pvgis-requests.mjs')
        if os.system(f"node {js_script_path} {tmp_dir_path}") != 0:
            raise Exception(f"{js_script_path} failed!")

    def __write_city_attributes_json(self, attribute_map, output_dir_path):
        json_name = "city-attributes.json"
        json_path = os.path.join(output_dir_path, json_name)

        with open(json_path, 'w') as fp:
            json.dump(attribute_map, fp)

        json_file_size_mb = get_file_size_mb(json_path)
        logging.info(f"City attributes JSON is {json_file_size_mb} MB")

    def __write_city_pv_json(self, pv_output_map, output_dir_path):
        json_name = "city-pv.json"
        json_path = os.path.join(output_dir_path, json_name)

        with open(json_path, 'w') as fp:
            json.dump(pv_output_map, fp)

        json_file_size_mb = get_file_size_mb(json_path)
        logging.info(f"City PV stats JSON is {json_file_size_mb} MB")

    def __convert_citygml_to_output_format(self, city_gml_file_path, output_dir_path):
        if self.output_format == "tiles":
            self.__convert_to_3d_tiles(city_gml_file_path, output_dir_path)

    def __convert_to_3d_tiles(self, processed_gml_path, output_dir_path):
        logging.info("Converting CityGML to 3D tiles")
        logging.info("Running convert.mjs")
        js_script_path = self.path_util.get_js_script('convert.mjs')
        if os.system(
                f"NODE_OPTIONS=--max-old-space-size=10000 node {js_script_path} {processed_gml_path} {output_dir_path}/") != 0:

            raise Exception(f"{js_script_path} failed!")

    def __update_tree(self, xml_building, attribs):
        gen = "ns3"

        for name, type, value in attribs:
            xml_tag = ET.SubElement(xml_building[0], f'{gen}:{type}')
            xml_tag.attrib["name"] = name
            xml_value = ET.SubElement(xml_tag, f'{gen}:value')
            xml_value.text = str(value)

    def extract_integer_id(self, string_id):
        subparts = string_id.split("_")
        return subparts[1]
