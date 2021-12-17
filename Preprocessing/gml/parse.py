import xml.etree.ElementTree as ET
from entites import Surface
from time import time
import json
import sys


CORE = "{http://www.opengis.net/citygml/2.0}"
GML = "{http://www.opengis.net/gml}"
GEN = "{http://www.opengis.net/citygml/generics/2.0}"
ID = "{http://www.opengis.net/gml}id"

FILE_PATH = "../../Data/citygml/lod1-tartu"


def get_roof_height(building):
    roof_height = 0.0

    for attribute in building.iter(f"{GEN}doubleAttribute"):
        if attribute.attrib["name"] == "z_max":
            height = attribute.find(f"{GEN}value").text
            roof_height = float(height)
            break
    
    return roof_height



def write_xml_area_elemet(building, area):
    element = ET.Element(f"{GEN}doubleAttribute", {"name": "area"})
    subelement = ET.Element(f"{GEN}value")
    subelement.text = str(area)

    element.append(subelement)
    building.append(element)


def process_buildings(buildings, mp):
    for building in buildings:
        id = building[0].attrib[ID]
        roof_height = get_roof_height(building)

        # https://epsg.io/3301, unit - meters
        for points_set in building.iter(f"{GML}posList"):
            surface = Surface(points_set.text)

            if surface.is_roof(roof_height):
                area = round(surface.area(), 3)
                mp[id] = area
                write_xml_area_elemet(building, area)
                break



def main():
    start = time()
    path = sys.argv[1]

    if not path:
        path = FILE_PATH

    tree = ET.parse(path)
    root = tree.getroot()

    mp = {}
    buildings = root.findall(f"{CORE}cityObjectMember")
    process_buildings(buildings, mp)

    tree.write(f"{FILE_PATH}-with-area.gml")
    with open('../../Cesium/public/model/areas.json', 'w') as fp:
        json.dump(mp, fp)

    duration = round(time() - start, 3)
    print(f"Time taken to add areas to Tartu city dataset: {duration}s")



if __name__ == "__main__":
    main()




