import json
import logging
import grequests
import time
import os

from lib.citygml.surface import Surface
from lib.citygml.building import Building
from lib.util.xml_constants import *
from lib.pipeline import Pipeline
from lib.solar_potential.formulas import calculate_peak_power_kpw, calculate_usable_area
from lib.solar_potential.pvgis import PvgisRequest
from collections import OrderedDict
from lib.util.timed import timed


class SolarPotentialPipeline(Pipeline):
    def run(self, level, pv_efficiency):
        logging.info("Running Solar Potential pipeline")
        self.pv_efficiency = pv_efficiency
        self.process_files(level, self.process)

    def process(self, tree, path_util, filename):
        buildings = tree.getroot().findall(f"{CORE}cityObjectMember")
        attribute_map = self.__get_building_attributes(buildings)
        self.__add_solar_potential_to_attribute_map(attribute_map)

        logging.info("Wrtiting to JSON")
        json_name = filename.replace(".gml", "")
        json_path = path_util.get_path_json(json_name)

        with open(json_path, 'w') as fp:
            json.dump(attribute_map, fp)

        json_file_size_mb = os.path.getsize(json_path) / 2 ** 20
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
        count_total = len(attribute_map)
        count_sent = 0

        request_batch_limit = 30
        batch = OrderedDict()
        failed_count = 0

        for key, data in attribute_map.items():
            roof_area = data["total_roof_area"]
            lat = data["lat"]
            lon = data["lon"]
            usable_roof_area = calculate_usable_area(roof_area)
            peak_power_kpw = calculate_peak_power_kpw(usable_roof_area, self.pv_efficiency)

            pv_calculations = PvgisRequest() \
                .set_location(lon, lat) \
                .set_peak_power_kwp(peak_power_kpw) \
                .set_mounting_place("building") \
                .optimize_angles() \
                .send_async()
            
            count_sent += 1
            batch[key] = pv_calculations
            
            if len(batch) == request_batch_limit:
                failed_count += self.__process_request_batch(batch, attribute_map)
                # not to hit rate limit
                time.sleep(1)
            
            if count_sent % 1000 == 0:
                logging.info(f"Sent {count_sent}/{count_total} requests")

        failed_count += self.__process_request_batch(batch, attribute_map)

        logging.info(f"{failed_count}/ {count_total} requests failed")
    
    def __process_request_batch(self, batch, attribute_map):
        keys = list(batch.keys())
        pv_data, failed_count = self.__process_pv_responses(batch)

        for i in range(len(keys)):
            building_id = keys[i]
            attribute_map[building_id]["solar_potential"] = pv_data[i]

        batch = OrderedDict()

        return failed_count


    # @timed("Processing PVGIS API responses")
    def __process_pv_responses(self, results):
        def exception_handler(request, exception):
            print(exception)

        pv_responses = grequests.map(results.values(), exception_handler=exception_handler)
        failed_count = 0
        output = []

        for resp in pv_responses:
            if not resp or not resp.ok:
                output.append({})
                failed_count += 1
            else:
                output.append(resp.json()["outputs"])

        return output, failed_count



            







