import xml.etree.ElementTree as ET
from entites import Surface

CORE = "{http://www.opengis.net/citygml/2.0}"
GML = "{http://www.opengis.net/gml}"
ID = "{http://www.opengis.net/gml}id"
GEN = "{http://www.opengis.net/citygml/generics/2.0}"

tree = ET.parse('../../Model/citygml/lod1-tartu_mini.gml')
root = tree.getroot()

area_dict = {}
buildings = root.findall(f"{CORE}cityObjectMember")

for building in buildings:
    id = building[0].attrib[ID]
    roof_height = 0.0

    for attribute in building.iter(f"{GEN}doubleAttribute"):
        if attribute.attrib["name"] == "z_max":
            height = attribute.find(f"{GEN}value").text
            roof_height = float(height)
            break

    for points in building.iter(f"{GML}posList"):
        surface = Surface(points.text)
        if surface.is_roof(roof_height):
            area_dict[id] = surface.area()


print(area_dict)



