import os
import xml.etree.ElementTree as ET
import json
import numpy as np
from enum import Enum
from lib.step import IStep
from lib.util.path import get_path_gml, get_path_json

CORE = "{http://www.opengis.net/citygml/2.0}"
GML = "{http://www.opengis.net/gml}"
GEN = "{http://www.opengis.net/citygml/generics/2.0}"
ID = "{http://www.opengis.net/gml}id"


class Level(Enum):
    LOD1 = 1
    LOD2 = 2


class Preprocessor(IStep):
    def __init__(self, file_gdrive_id, level):
        self.__file_gdrive_id = file_gdrive_id
        self.__level = level

    def execute(self):
        print("Parsing GML and extracting useful info...")

        path = get_path_gml(self.__file_gdrive_id)
        tree = ET.parse(path)
        root = tree.getroot()

        attribute_map = {}
        buildings = root.findall(f"{CORE}cityObjectMember")
        self.__process_buildings(buildings, attribute_map)

        with open(get_path_json(self.__file_gdrive_id), 'w') as fp:
            json.dump(attribute_map, fp)


    def cleanup(self):
        os.remove(get_path_gml(self.__file_gdrive_id))


    def __process_buildings(self, buildings, attribute_map):
        for building in buildings:
            id = building[0].attrib[ID]
            roof_height = self.__get_roof_height(building)
            attribute_map[id] = attribute_map.get(id, {})

            # https://epsg.io/3301, unit - meters
            for points_set in building.iter(f"{GML}posList"):
                surface = Surface(points_set.text)

                should_process_lod1 = self.__level == Level.LOD1 and surface.is_lod1_roof(roof_height)
                should_process_lod2 = self.__level == Level.LOD2 and surface.is_lod2_roof(roof_height)

                if should_process_lod1 or should_process_lod2:
                    area = surface.area()
                    incline = surface.incline()
                    attribute_map[id]["roofs"] = attribute_map[id].get("roofs", [])
                    attribute_map[id]["roofs"].append({"area": area, "incline": incline})

    
    def __get_roof_height(self, building):
        roof_height = 0.0

        for attribute in building.iter(f"{GEN}doubleAttribute"):
            if attribute.attrib["name"] == "z_max":
                height = attribute.find(f"{GEN}value").text
                roof_height = float(height)
                break
        
        return roof_height



class Surface:
    def __init__(self, points_str: str) -> None:
        self.points: list[list[float]] = []
        self.__add_points(points_str)

        
    def __add_points(self, points_str: str) -> None:
        floats = [float(e) for e in points_str.split(" ")]
        divisions = len(floats) // 3

        for i in range(divisions):
            # add every 3 values
            self.points.append((floats[i * 3: (i + 1) * 3]))


    def is_lod1_roof(self, roof_height) -> bool:
        is_roof = True
        for point in self.points:
            if point.z != roof_height:
                is_roof = False
                break
        
        return is_roof
    

    def is_lod2_roof(self, roof_height) -> bool:
        return False

    # https://stackoverflow.com/questions/12642256/find-area-of-polygon-from-xyz-coordinates
    def area(self):
        #all edges
        edges = self.points[1:] - self.points[0:1]
        # row wise cross product
        cross_product = np.cross(edges[:-1],edges[1:], axis=1)
        #area of all triangles
        area = np.linalg.norm(cross_product, axis=1) / 2
        return sum(area)
