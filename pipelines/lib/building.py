from lib.xml_constants import *


class Building:
    def __init__(self, id, xml_building):
        self.id = id
        self.xml_building = xml_building

    def get_surface_points(self):
        return self.xml_building.iter(f"{GML}posList")

    def get_z_min(self):
        for attribute in self.xml_building.iter(f"{GEN}doubleAttribute"):
            if attribute.attrib["name"] == "z_min":
                return float(attribute[0].text)

        return 0
