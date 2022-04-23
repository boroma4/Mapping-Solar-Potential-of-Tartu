from lib.util.xml_constants import *
from pyproj import Proj, transform

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
    
    def get_approx_lat_lon(self):
        first_surface_str = list(self.get_surface_points())[0].text
        x, y = list(map(float, first_surface_str.split(" ")[:2]))

        # TODO: make dynamic based on the file
        return transform(Proj('EPSG:3301'), Proj('EPSG:4326'), x, y)
