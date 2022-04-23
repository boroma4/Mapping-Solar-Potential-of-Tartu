import json
import logging
import os

from lib.citygml.surface import Surface
from lib.citygml.building import Building
from lib.util.xml_constants import *
from lib.pipeline import Pipeline
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

        logging.info("Wrtiting results to JSON")
        json_name = filename.replace(".gml", "")
        json_path = path_util.get_path_json(json_name)

        with open(json_path, 'w') as fp:
            json.dump(attribute_map, fp)

        json_file_size_mb = get_file_size_mb(json_path)
        logging.info(f"City attributes JSON is {json_file_size_mb} MB")

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

            # https://epsg.io/3301, unit - meters
            for points in building.get_surface_points():
                surface = Surface(points.text)

                if surface.is_roof(z_min):
                    area = surface.area()
                    azimuth, tilt = surface.angles()

                    attribute_map[id]["roofs"] = attribute_map[id].get("roofs", [])
                    roof_attribs = {"area": area, "azimuth": azimuth, "tilt": tilt}

                    if roof_attribs not in attribute_map[id]["roofs"]:
                        attribute_map[id]["roofs"].append(roof_attribs)

            if "roofs" not in attribute_map[id]:
                count_no_roofs += 1
                attribute_map[id]["roofs"] = [{"area": 0, "azimuth": 0, "tilt": 0}]

            total_roof_area = sum([roof["area"] for roof in attribute_map[id]["roofs"]])
            lat, lon = building.get_approx_lat_lon()

            attribute_map[id]["total_roof_area"] = total_roof_area
            attribute_map[id]["lat"] = lat
            attribute_map[id]["lon"] = lon

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
            attribute_map[id] = {"building": attribute_map[id], "pv": pv_data[id]}
        
        return attribute_map

    @timed("Sending requests to PVGIS from Node.js")
    def __send_pvgis_api_requests(self):
        logging.info("Running batch-pvgis-requests.mjs")
        tmp_dir_path = self.path_util.get_tmp_dir_path()
        js_script_path = self.path_util.get_js_script('batch-pvgis-requests.mjs')
        os.system(f"node {js_script_path} {tmp_dir_path}")