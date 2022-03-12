import os
import xml.etree.ElementTree as ET
import json
import functools

from lib.util.path import PathUtil
from lib.util.lod import Level
from lib.util.surface import Surface

CORE = "{http://www.opengis.net/citygml/2.0}"
GML = "{http://www.opengis.net/gml}"
GEN = "{http://www.opengis.net/citygml/generics/2.0}"
ID = "{http://www.opengis.net/gml}id"


class Preprocessor():

    def process(self, level):
        path_util = PathUtil(level)
        data_dir_path = path_util.get_data_dir_path()

        for filename in os.listdir(data_dir_path):
            file_path = os.path.join(data_dir_path, filename)

            if os.path.isfile(file_path) and file_path.endswith(".gml"):
                print(f'Processing {filename}, level: {level}')

                tree = ET.parse(file_path)
                root = tree.getroot()

                attribute_map = {}
                buildings = root.findall(f"{CORE}cityObjectMember")
                self.__process_buildings(buildings, attribute_map, level)

                new_file_path = os.path.join(data_dir_path, f"updated-{filename}")
                tree.write(new_file_path)

                json_name = filename.replace(".gml", "")
                
                with open(path_util.get_path_json(json_name), 'w') as fp:
                    json.dump(attribute_map, fp)
                
                print("Done\n")
            else:
                print(f'Ignoring file: {file_path}')


    def __process_buildings(self, buildings, attribute_map, level):
        count_total = 0
        count_no_roofs = 0

        for building in buildings:
            id = building[0].attrib[ID]
            roof_height = self.__get_roof_height(building)
            attribute_map[id] = attribute_map.get(id, {})

            # https://epsg.io/3301, unit - meters
            for points_set in building.iter(f"{GML}posList"):
                surface = Surface(points_set.text)

                should_process_lod1 = level == Level.LOD1 and surface.is_lod1_roof(roof_height)
                should_process_lod2 = level == Level.LOD2 and surface.is_lod2_roof(roof_height)

                if should_process_lod1 or should_process_lod2:
                    area = surface.area()
                    incline = surface.incline()

                    # For writing to separate JSON
                    attribute_map[id]["roofs"] = attribute_map[id].get("roofs", [])
                    attribute_map[id]["roofs"].append({"area": area, "incline": incline})
            
            count_total += 1
            if "roofs" not in attribute_map[id]:
                count_no_roofs += 1
                continue

            self.__update_tree(building, attribute_map, id)
        
        print(f"Roofs not detected for {count_no_roofs}/{count_total} buildings")


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
    
    def __get_roof_height(self, building):
        roof_height = 0.0

        for attribute in building.iter(f"{GEN}doubleAttribute"):
            if attribute.attrib["name"] == "z_max":
                height = attribute.find(f"{GEN}value").text
                roof_height = float(height)
                break
        
        return roof_height