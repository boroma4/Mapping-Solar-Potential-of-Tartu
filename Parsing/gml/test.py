import xml.etree.ElementTree as ET

CORE = "{http://www.opengis.net/citygml/2.0}"
GML = "{http://www.opengis.net/gml}"
ID = "{http://www.opengis.net/gml}id"

tree = ET.parse('../../Model/citygml/tartu_mini.gml')
r = tree.getroot()

area_dict = {}
buildings = r.findall(f"{CORE}cityObjectMember")

for building in buildings:
    #points = b.findall(f"{GML}posList")
    id = building[0].attrib[ID]
    for surface in building.iter(f"{GML}LinearRing"):
        #print(a.tag)
        for points in surface.iter(f"{GML}posList"):
            area = points.text[0:5]
            area_dict[id] = area


print(area_dict)



