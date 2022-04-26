import json
import logging
import os
import xml.etree.ElementTree as ET

from lib.citygml.surface import Surface
from lib.citygml.building import Building
from lib.util.xml_constants import *
from lib.pipeline import Pipeline, UPDATED_PREFIX
from lib.solar_potential.formulas import calculate_peak_power_kpw, calculate_usable_area
from lib.solar_potential.pvgis_request_builder import PvgisRequestBuilder
from lib.util.decorators import timed
from lib.util.file_size import get_file_size_mb


class SolarPotentialPipeline(Pipeline):
    def run(self, level, pv_efficiency, pv_loss):
        logging.info("Running Solar Potential pipeline")
        self.pv_efficiency = pv_efficiency
        self.pv_loss = pv_loss
        self.process_files(level, self.process)

    def process(self, tree, path_util, filename):
        self.path_util = path_util
        buildings = tree.getroot().findall(f"{CORE}cityObjectMember")
        attribute_map = self.__get_building_attributes(buildings)
        attribute_map = self.__add_solar_potential_to_attribute_map(attribute_map)
        self.__write_solar_output_to_tree(buildings, attribute_map)
        pv_output_map = self.__calculate_solar_stats(attribute_map)

        original_file_path = path_util.get_path_gml(filename)
        processed_file_path = path_util.get_path_gml(f"{UPDATED_PREFIX}{filename}")

        logging.info("Updating XML tree")
        tree.write(processed_file_path)

        logging.info("Converting CityGML to 3D tiles")

        output_dir_path = original_file_path.removesuffix(".gml") + "-output"
        if not os.path.exists(output_dir_path):
            os.mkdir(output_dir_path)

        logging.info("Running convert.mjs")
        js_script_path = path_util.get_js_script('convert.mjs')
        os.system(
            f"NODE_OPTIONS=--max-old-space-size=10000 node {js_script_path} {processed_file_path} {output_dir_path}/")
        
        logging.info("Wrtiting results to JSON")
        json_name = "city-attributes.json"
        json_path = os.path.join(output_dir_path, json_name)

        with open(json_path, 'w') as fp:
            json.dump(attribute_map, fp)

        json_file_size_mb = get_file_size_mb(json_path)
        logging.info(f"City attributes JSON is {json_file_size_mb} MB")

        json_name = "city-pv.json"
        json_path = os.path.join(output_dir_path, json_name)

        with open(json_path, 'w') as fp:
            json.dump(pv_output_map, fp)

        json_file_size_mb = get_file_size_mb(json_path)
        logging.info(f"City PV stats JSON is {json_file_size_mb} MB")

    @timed("Building analysis")
    def __get_building_attributes(self, buildings):
        count_total = len(buildings)
        count_processed = 0
        count_no_roofs = 0
        attribute_map = {}

        logging.info("Getting useful attributes of the buildings")

        for xml_building in buildings:
            id = self.extract_id(xml_building[0].attrib[ID])
            building = Building(id, xml_building)
            attribute_map[id] = attribute_map.get(id, {})
            z_min = building.get_z_min()

            attribute_map[id]["roofs"] = []
            # https://epsg.io/3301, unit - meters
            for points in building.get_surface_points():
                surface = Surface(points.text)

                if surface.is_roof(z_min):
                    area = surface.area()
                    azimuth, tilt = surface.angles()

                    roof_attribs = {"area": area, "azimuth": azimuth, "tilt": tilt}

                    if roof_attribs not in attribute_map[id]["roofs"]:
                        attribute_map[id]["roofs"].append(roof_attribs)

            if "roofs" not in attribute_map[id]:
                count_no_roofs += 1
                attribute_map[id]["roofs"] = [{"area": 0, "azimuth": 0, "tilt": 0}]

            total_roof_area = sum([roof["area"] for roof in attribute_map[id]["roofs"]])
            lat, lon = building.get_approx_lat_lon()

            attribute_map[id]["total_roof_area"] = round(total_roof_area, 2)
            attribute_map[id]["lat"] = lat
            attribute_map[id]["lon"] = lon
            self.__update_tree(xml_building, [["area", "doubleAttribute", total_roof_area], ["etak_id", "stringAttribute", id]])


            count_processed += 1
            if count_processed % 5000 == 0:
                logging.info(f"Processed {count_processed}/{count_total} buildings")

        logging.info(
            f"Roofs not detected for {count_no_roofs}/{count_total} buildings")

        return attribute_map

    @timed("PVGIS requests")
    def __add_solar_potential_to_attribute_map(self, attribute_map):
        logging.info("Obtaining solar potential from PVGIS API")
        payload_map = {}

        for id, data in attribute_map.items():
            roof_area = data["total_roof_area"]
            lat = data["lat"]
            lon = data["lon"]
            usable_roof_area = calculate_usable_area(roof_area)
            peak_power_kpw = calculate_peak_power_kpw(usable_roof_area, self.pv_efficiency)

            payload = PvgisRequestBuilder() \
                .set_location(lon, lat) \
                .set_peak_power_kwp(peak_power_kpw) \
                .set_mounting_place("building") \
                .set_loss(self.pv_loss) \
                .optimize_angles() \
                .get_payload()

            payload_map[id] = payload

        logging.info("Storing requests data to be processed by Node.js script")
        tmp_dir_path = self.path_util.get_tmp_dir_path()
        requests_json_path = tmp_dir_path + "/requests.json"

        with open(requests_json_path, 'w') as fp:
            json.dump(payload_map, fp)
            logging.info(f"File created: {requests_json_path}")

        self.__send_pvgis_api_requests()

        responses_json_path = tmp_dir_path + "/responses.json"
        json_file_size_mb = get_file_size_mb(responses_json_path)
        logging.info(f"Responses JSON is {json_file_size_mb} MB")

        with open(responses_json_path, 'r') as fp:
            pv_data = json.loads(fp.read())
        
        for id in attribute_map.keys():
            # If building area is 0, request to the API will return an error instead of data and it won't be added to responses json
            if id not in pv_data:
                pv_data[id] = {"totals": {"fixed": {"E_y": 0}}}
                pv_data[id]["totals"]["fixed"]["E_m_exact"] = []
                pv_data[id]["monthly"] = {}
                pv_data[id]["monthly"]["fixed"] = []
                for i in range(12):
                    pv_data[id]["totals"]["fixed"]["E_m_exact"].append(0)
                    pv_data[id]["monthly"]["fixed"].append({"E_m": 0})

            pv_data[id]["totals"]["fixed"]["E_m_exact"] = []
            for i in range(12):
                pv_data[id]["totals"]["fixed"]["E_m_exact"].append(pv_data[id]["monthly"]["fixed"][i]["E_m"])

            attribute_map[id] = {"building": attribute_map[id], "pv": pv_data[id]["totals"]["fixed"]}
        
        return attribute_map
    

    @timed("Updating the XML tree with solar data")
    def __write_solar_output_to_tree(self, buildings, attribute_map):
        for xml_building in buildings:
            id = self.extract_id(xml_building[0].attrib[ID])
            self.__update_tree(xml_building, [["power", "doubleAttribute", attribute_map[id]["pv"]["E_y"]]])


    @timed("Sending requests to PVGIS from Node.js")
    def __send_pvgis_api_requests(self):
        logging.info("Running batch-pvgis-requests.mjs")
        tmp_dir_path = self.path_util.get_tmp_dir_path()
        js_script_path = self.path_util.get_js_script('batch-pvgis-requests.mjs')
        os.system(f"node {js_script_path} {tmp_dir_path}")
    

    def __update_tree(self, xml_building, attribs):
        gen = "ns3"

        for name, type, value in attribs:
            xml_tag = ET.SubElement(xml_building[0], f'{gen}:{type}')
            xml_tag.attrib["name"] = name
            xml_value = ET.SubElement(xml_tag, f'{gen}:value')
            xml_value.text = str(value)
    

    def __calculate_solar_stats(self, attribute_map):
        output = {}
        output["total_yearly_energy_kwh"] = round(sum([el["pv"]["E_y"] for el in attribute_map.values()]), 3)
        output["total_monthly_energy_kwh_list"] = [round(sum([el["pv"]["E_m_exact"][i] for el in attribute_map.values()]), 3) for i in range(12)]

        return output