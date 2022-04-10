import os
import xml.etree.ElementTree as ET
import json
import logging
import time

from lib.util.path import PathUtil
from lib.util.lod import Level
from lib.util.surface import Surface

CORE = "{http://www.opengis.net/citygml/2.0}"
GML = "{http://www.opengis.net/gml}"
GEN = "{http://www.opengis.net/citygml/generics/2.0}"
ID = "{http://www.opengis.net/gml}id"

UPDATED_PREFIX = "updated-"

class Preprocessor():

    def __init__(self, data_path) -> None:
        self.data_path = data_path

    def process(self, level):
        path_util = PathUtil(self.data_path, level)
        data_dir_path = path_util.get_data_dir_path()

        for filename in os.listdir(data_dir_path):
            file_path = os.path.join(data_dir_path, filename)
            is_valid_prefix_and_suffix = file_path.endswith(".gml") and not filename.startswith(UPDATED_PREFIX)

            if os.path.isfile(file_path) and is_valid_prefix_and_suffix:
                logging.info(f'Processing {filename}, level: {level}')
                start_time = time.time()

                tree = ET.parse(file_path)
                root = tree.getroot()

                attribute_map = {}
                buildings = root.findall(f"{CORE}cityObjectMember")
                self.__process_buildings(buildings, attribute_map, level)

                new_file_path = os.path.join(data_dir_path, f"{UPDATED_PREFIX}{filename}")
                tree.write(new_file_path)

                json_name = filename.replace(".gml", "")

                with open(path_util.get_path_json(json_name), 'w') as fp:
                    json.dump(attribute_map, fp)
                
                end_time = time.time()
                duration = round(end_time - start_time, 3)

                logging.info(f"Done. Took {duration}s\n")
            else:
                logging.info(f'Ignoring file: {file_path}\n')


    def __process_buildings(self, buildings, attribute_map, level):
        count_total = 0
        count_no_roofs = 0

        for building in buildings:
            id = building[0].attrib[ID]
            maximum, minimum = self.__get_z_range(building)
            attribute_map[id] = attribute_map.get(id, {})

            # https://epsg.io/3301, unit - meters
            for points in building.iter(f"{GML}posList"):
                surface = Surface(points.text)

                if surface.is_roof(maximum, minimum):
                    area = surface.area()
                    azimuth, tilt = surface.angles()

                    # For writing to separate JSON
                    attribute_map[id]["roofs"] = attribute_map[id].get("roofs", [])
                    attribute_map[id]["roofs"].append({"area": area, "azimuth": azimuth, "tilt": tilt})

            
            count_total += 1

            if "roofs" not in attribute_map[id]:
                count_no_roofs += 1
                attribute_map[id]["roofs"] = [{"area": 0, "azimuth": 0, "tilt": 0}]

            self.__update_tree(building, attribute_map, id)
        
        logging.info(f"Roofs not detected for {count_no_roofs}/{count_total} buildings")


    def __update_tree(self, building, attributes, id):
        gen = "ns3"
        roofs = attributes[id]["roofs"]
        total_roof_area = 0

        for roof in roofs:
            total_roof_area += roof["area"]

        id_tag = ET.SubElement(building[0], f'{gen}:stringAttribute')
        area_tag = ET.SubElement(building[0], f'{gen}:doubleAttribute')

        id_tag.attrib["name"] = "str_id"
        area_tag.attrib["name"] = "area"

        id_tag_value = ET.SubElement(id_tag, f'{gen}:value')
        area_tag_value = ET.SubElement(area_tag, f'{gen}:value')

        id_tag_value.text = id
        area_tag_value.text = f'{total_roof_area}'
    
    def __get_z_range(self, building):
        maximum, minimum = 0, 0

        for attribute in building.iter(f"{GEN}doubleAttribute"):
            if attribute.attrib["name"] == "z_max":
                maximum = float(attribute[0].text)
            if attribute.attrib["name"] == "z_min":
                minimum = float(attribute[0].text)
        
        return maximum, minimum