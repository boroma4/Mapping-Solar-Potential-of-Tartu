from lib.xml_constants import *
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

    def get_address_element(self):
        return self.get_single_generic_subelement(
            self.xml_building, f'{BLDG}address')

    def get_lat_lon(self):
        address = self.get_address_element()
        loc = self.get_single_generic_subelement(address, f"{GML}MultiPoint")
        srcName = loc.attrib["srsName"].lower()

        location_points = self.get_single_generic_subelement(
            loc, f"{GML}pos").text.split(" ")
        x, y = list(map(float, location_points[:2]))

        inProj = Proj(srcName)
        outProj = Proj('epsg:4326')

        return transform(inProj, outProj, x, y)

    def get_single_generic_subelement(self, parent, tag):
        elements = list(parent.iter(tag))

        if len(elements) != 1:
            raise Exception(
                f"Invalid get_single_generic_subelement method call, {tag} has {len(elements)} copies, building id: {self.id}")

        return elements[0]
