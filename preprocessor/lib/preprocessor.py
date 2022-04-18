import os
import xml.etree.ElementTree as ET
import json
import logging
import time

from lib.util.path import PathUtil
from lib.util.surface import Surface
from lib.building import Building
from lib.xml_constants import *

UPDATED_PREFIX = "updated-"


class Preprocessor():

    def __init__(self, data_path) -> None:
        self.data_path = data_path

    def process(self, level):
        path_util = PathUtil(self.data_path, level)
        data_dir_path = path_util.get_data_dir_path()

        for filename in os.listdir(data_dir_path):
            file_path = os.path.join(data_dir_path, filename)
            is_valid_prefix_and_suffix = file_path.endswith(
                ".gml") and not filename.startswith(UPDATED_PREFIX)

            if os.path.isfile(file_path) and is_valid_prefix_and_suffix:
                logging.info(f'Processing {filename}, level: {level}')
                start_time = time.time()

                tree = ET.parse(file_path)
                root = tree.getroot()

                attribute_map = {}
                buildings = root.findall(f"{CORE}cityObjectMember")
                self.__process_buildings(buildings, attribute_map)

                new_file_path = os.path.join(
                    data_dir_path, f"{UPDATED_PREFIX}{filename}")

                logging.info("Updating XML tree")
                tree.write(new_file_path)

                logging.info("Wrtiting to JSON")
                json_name = filename.replace(".gml", "")

                with open(path_util.get_path_json(json_name), 'w') as fp:
                    json.dump(attribute_map, fp)

                end_time = time.time()
                duration = round(end_time - start_time, 3)

                logging.info(f"Done. Took {duration}s\n")
            else:
                logging.info(f'Ignoring file: {file_path}\n')

    def __process_buildings(self, buildings, attribute_map):
        count_total = len(buildings)
        count_no_roofs = 0
        count_no_location = 0

        for xml_building in buildings:
            id = self.__extract_id(xml_building[0].attrib[ID])
            building = Building(id, xml_building)
            attribute_map[id] = attribute_map.get(id, {})
            z_min = building.get_z_min()

            # https://epsg.io/3301, unit - meters
            for points in building.get_surface_points():
                surface = Surface(points.text)

                if surface.is_roof(z_min):
                    area = surface.area()
                    azimuth, tilt = surface.angles()

                    # For writing to separate JSON
                    attribute_map[id]["roofs"] = attribute_map[id].get("roofs", [])

                    roof_attribs = {"area": area, "azimuth": azimuth, "tilt": tilt}

                    if roof_attribs not in attribute_map[id]["roofs"]:
                        attribute_map[id]["roofs"].append(roof_attribs)

            if "roofs" not in attribute_map[id]:
                count_no_roofs += 1
                attribute_map[id]["roofs"] = [{"area": 0, "azimuth": 0, "tilt": 0}]

            total_roof_area = sum([roof["area"] for roof in attribute_map[id]["roofs"]])
            lat, lon = 0, 0

            try:
                lat, lon = building.get_lat_lon()
            except BaseException:
                # TODO: take random surface point
                count_no_location += 1

            attribute_map[id]["total_roof_area"] = total_roof_area
            attribute_map[id]["lat"] = lat
            attribute_map[id]["lon"] = lon

            self.__update_tree(xml_building, total_roof_area, id)

        logging.info(
            f"Roofs not detected for {count_no_roofs}/{count_total} buildings")
        logging.info(
            f"No location specified for {count_no_location}/{count_total} buildings")

    def __update_tree(self, xml_building, total_roof_area, id):
        gen = "ns3"

        id_tag = ET.SubElement(xml_building[0], f'{gen}:stringAttribute')
        area_tag = ET.SubElement(xml_building[0], f'{gen}:doubleAttribute')

        id_tag.attrib["name"] = "str_id"
        area_tag.attrib["name"] = "area"

        id_tag_value = ET.SubElement(id_tag, f'{gen}:value')
        area_tag_value = ET.SubElement(area_tag, f'{gen}:value')

        id_tag_value.text = id
        area_tag_value.text = f'{total_roof_area}'

    def __extract_id(self, string_id):
        subparts = string_id.split("_")
        return subparts[1]
