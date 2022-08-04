import logging
import os
import xml.etree.ElementTree as ET

from lib.citygml.building import Building
from lib.util.constants import *
from lib.pipeline import Pipeline, UPDATED_PREFIX
from lib.solar_potential.pvgis_api import PvgisRequestBuilder, make_empty_response
from lib.util.decorators import timed
from lib.util import file_util
from lib.util.lod import Level
from lib.util.path import PathUtil


class SolarPotentialPipeline(Pipeline):
    def __init__(self, single_file_name: str, level: Level, pv_efficiency: float, pv_loss: float,
                 roof_coverage: float, optimize_2d: bool, output_format: str, node_ram_limit: int) -> None:
        super().__init__(single_file_name)
        self.level = level
        self.pv_efficiency = pv_efficiency
        self.pv_loss = pv_loss
        self.roof_coverage = roof_coverage
        self.optimize_2d = optimize_2d
        self.output_format = output_format
        self.node_ram_limit = node_ram_limit

    def run(self) -> None:
        logging.info("Running Solar Potential pipeline")
        self.process_files(self.level, self.process_city_gml_file)

    def process_city_gml_file(self, tree: ET.ElementTree, path_util: PathUtil, filename: str) -> None:
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
        file_util.write_json(attribute_map, output_dir_path, "city-attributes.json")
        file_util.write_json(pv_output_map, output_dir_path, "city-pv.json")

        # Converting CityGML to visualizable format
        self.__convert_citygml_to_output_format(processed_file_path, output_dir_path)

        logging.info(f'Output files can be located at {output_dir_path}')

    @timed("Building analysis")
    def __get_building_attributes(self, buildings: list[ET.Element]) -> dict:
        count_total_buildings = len(buildings)
        count_processed_buildings = 0
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
                roof_attribs = {
                    "id": count_roofs,
                    "area": surface.area,
                    "azimuth": surface.azimuth,
                    "tilt": surface.tilt,
                    "orientation": surface.orientation,
                    "points_epsg_3301": surface.points
                }

                # handling duplicated points
                if roof_attribs not in attribute_map[building_id]["roofs"]:
                    attribute_map[building_id]["roofs"].append(roof_attribs)

            building_attributes = attribute_map[building_id]
            roofs = building_attributes["roofs"]

            if len(roofs) == 0:
                count_no_roofs += 1

            total_roof_area = round(sum([roof["area"] for roof in roofs]), 3)
            oriented_areas = {}
            lat, lon = building.get_approx_lat_lon()

            for orientation in ORIENTATIONS:
                areas = [roof["area"] for roof in roofs if roof["orientation"] == orientation]
                oriented_areas[orientation] = round(sum(areas), 3)

            building_attributes["total_roof_area"] = round(total_roof_area, 2)
            building_attributes["lat"] = lat
            building_attributes["lon"] = lon

            self.__update_tree(xml_building, [
                ["etak_id", "stringAttribute", building_id],
                ["area", "doubleAttribute", total_roof_area],
                ["north-area", "doubleAttribute", oriented_areas[NORTH]],
                ["south-area", "doubleAttribute", oriented_areas[SOUTH]],
                ["west-area", "doubleAttribute", oriented_areas[WEST]],
                ["east-area", "doubleAttribute", oriented_areas[EAST]],
                ["flat-area", "doubleAttribute", oriented_areas[NONE]]])

            count_processed_buildings += 1
            if count_processed_buildings % 5000 == 0:
                logging.info(f"Processed {count_processed_buildings}/{count_total_buildings} buildings")

        logging.info(
            f"Roofs not detected for {count_no_roofs}/{count_total_buildings} buildings")
        logging.info(f"{count_roofs} roof surfaces detected")

        return attribute_map

    @timed("Estimating solar potential through PVGIS requests")
    def __add_solar_potential_to_attribute_map(self, attribute_map: dict) -> dict:
        logging.info("Obtaining solar potential from PVGIS API")
        payload_map = {}

        # For each building an array of it's roof surfaces is processed
        for building_id, building_data in attribute_map.items():
            payload_map[building_id] = []

            for roof in building_data["roofs"]:
                roof_id = roof["id"]
                roof_area = roof["area"]
                orientation = roof["orientation"]
                lat = building_data["lat"]
                lon = building_data["lon"]

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
                if roof["tilt"] <= MAX_FLAT_SURFACE_TILT:
                    request_builder.optimize_angles()

                request_data = [roof_id, orientation, request_builder.get_payload()]
                payload_map[building_id].append(request_data)

        logging.info("Storing requests data to be processed by Node.js script")

        tmp_dir_path = self.path_util.get_tmp_dir_path()
        file_util.write_json(payload_map, tmp_dir_path, "requests.json")

        # calls the Node.js script which saves results to a new json file
        self.__send_pvgis_api_requests()

        pv_data = file_util.read_json(tmp_dir_path, "responses.json")

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
            roofs_pv_list = [
                data["totals"]["fixed"] | {
                    "orientation": data["orientation"], "roof_id": data["roofId"]} for data in pv_data[building_id]]

            # In case yearly energy is None
            for roof_pv in roofs_pv_list:
                roof_pv["E_y"] = roof_pv["E_y"] or 0

            
            # variables:
            # 'E_d': {'description': 'Average daily energy production from the given system', 'units': 'kWh/d'},
            # 'E_m': {'description': 'Average monthly energy production from the given system', 'units': 'kWh/mo'},
            # 'E_y': {'description': 'Average annual energy production from the given system', 'units': 'kWh/y'},
            # 'H(i)_d': {'description': 'Average daily sum of global irradiation per square meter received by the modules of the given system', 'units': 'kWh/m2/d'},
            # 'H(i)_m': {'description': 'Average monthly sum of global irradiation per square meter received by the modules of the given system', 'units': 'kWh/m2/mo'},
            # 'H(i)_y': {'description': 'Average annual sum of global irradiation per square meter received by the modules of the given system', 'units': 'kWh/m2/y'},
            # 'SD_m': {'description': 'Standard deviation of the monthly energy production due to year-to-year variation', 'units': 'kWh'},
            # 'SD_y': {'description': 'Standard deviation of the annual energy production due to year-to-year variation', 'units': 'kWh'},
            # 'l_aoi': {'description': 'Angle of incidence loss', 'units': '%'},
            # 'l_spec': {'description': 'Spectral loss', 'units': '%'},
            # 'l_tg': {'description': 'Temperature and irradiance loss', 'units': '%'},
            # 'l_total': {'description': 'Total loss', 'units': '%'}

            # Merge geo and geometry data with PV data by roof id in O(n*m) - not optimal
            for roof in attribute_map[building_id]["roofs"]:
                for roof_pv in roofs_pv_list:
                    if roof["id"] == roof_pv["roof_id"]:
                        roof["yearly_kwh"] = roof_pv["E_y"]
                        roof["monthly_average_kwh"] = roof_pv["E_m"]
                        roof["monthly_kwh"] = roof_pv["E_m_exact"]
                        roof["total_loss"] = roof_pv["l_total"]


            # Requests that errored are not returned, writing no data here
            for roof in attribute_map[building_id]["roofs"]:
                roof["yearly_kwh"] = roof.get("yearly_kwh", 0)
                roof["monthly_average_kwh"] = roof.get("monthly_average_kwh", 0)
                roof["monthly_kwh"] = roof.get("monthly_kwh", [0] * 12)
                roof["total_loss"] =  roof.get("total_loss", 0)

        return attribute_map

    # Calculates estimated monthly and yearly energy production for the whole city

    def __calculate_city_solar_stats(self, attribute_map: dict) -> dict:
        output = {}
        total_yearly = 0
        total_monthly = [0] * 12

        for building_data in attribute_map.values():
            total_yearly += round(sum([el["yearly_kwh"] for el in building_data["roofs"]]), 3)
            for month in range(12):
                total_monthly[month] += round(sum([el["monthly_kwh"][month] for el in building_data["roofs"]]), 3)

        output["total_yearly_energy_kwh"] = total_yearly
        output["total_monthly_energy_kwh_list"] = total_monthly
        return output

    @timed("Updating the XML tree with solar data")
    def __write_solar_output_to_tree(self, buildings: list[ET.Element], attribute_map: dict) -> None:
        for xml_building in buildings:
            id = self.extract_integer_id(xml_building[0].attrib[ID])
            building_data = attribute_map[id]

            total_yearly_power = round(sum([roof["yearly_kwh"] for roof in building_data["roofs"]]), 3)
            oriented_power = {}

            for orientation in ORIENTATIONS:
                power_list = [roof["yearly_kwh"] for roof in building_data["roofs"] if roof["orientation"] == orientation]
                oriented_power[orientation] = round(sum(power_list), 3)

            self.__update_tree(xml_building, [
                ["power", "doubleAttribute", total_yearly_power],
                ["north-power", "doubleAttribute", oriented_power[NORTH]],
                ["south-power", "doubleAttribute", oriented_power[SOUTH]],
                ["west-power", "doubleAttribute", oriented_power[WEST]],
                ["east-power", "doubleAttribute", oriented_power[EAST]],
                ["optimized-power", "doubleAttribute", oriented_power[NONE]],
            ])

    @timed("Converting CityGML to another format")
    def __convert_citygml_to_output_format(self, city_gml_file_path, output_dir_path) -> None:
        if self.output_format == "tiles":
            self.__convert_to_3d_tiles(city_gml_file_path, output_dir_path)

    def __send_pvgis_api_requests(self) -> None:
        logging.info("Running batch-pvgis-requests.mjs")
        tmp_dir_path = self.path_util.get_tmp_dir_path()
        js_script_path = self.path_util.get_js_script('batch-pvgis-requests.mjs')
        if os.system(f"node {js_script_path} {tmp_dir_path}") != 0:
            raise Exception(f"{js_script_path} failed!")

    def __convert_to_3d_tiles(self, processed_gml_path, output_dir_path) -> None:
        logging.info("Converting CityGML to 3D tiles")
        logging.info("Running convert.mjs")
        js_script_path = self.path_util.get_js_script('convert.mjs')
        if os.system(
                f"NODE_OPTIONS=--max-old-space-size={self.node_ram_limit} node {js_script_path} {processed_gml_path} {output_dir_path}/") != 0:

            raise Exception(f"{js_script_path} failed!")

    def __update_tree(self, xml_building: ET.Element, attribs: list[tuple[str, str, str]]) -> None:
        gen = "ns3"

        for name, type, value in attribs:
            xml_tag = ET.SubElement(xml_building[0], f'{gen}:{type}')
            xml_tag.attrib["name"] = name
            xml_value = ET.SubElement(xml_tag, f'{gen}:value')
            xml_value.text = str(value)

    def extract_integer_id(self, string_id: str) -> str:
        subparts = string_id.split("_")
        return subparts[1]
