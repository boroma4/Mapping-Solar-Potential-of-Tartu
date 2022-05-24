from lib.util.xml_constants import *
from pyproj import Proj, transform
from lib.citygml.surface import Surface


class Building:
    def __init__(self, id, xml_building):
        self.id = id
        self.xml_building = xml_building

    def get_surfaces(self):
        return [Surface(points) for points in self.xml_building.iter(f"{GML}posList")]

    def get_z_min(self):
        for attribute in self.xml_building.iter(f"{GEN}doubleAttribute"):
            if attribute.attrib["name"] == "z_min":
                return float(attribute[0].text)

        return 0

    def get_approx_lat_lon(self):
        first_surface = list(self.get_surfaces())[0]
        points = first_surface.points[0]
        x, y = points[:2]

        # TODO: make dynamic based on the file
        return transform(Proj('EPSG:3301'), Proj('EPSG:4326'), x, y)

    def optimize_for_2d_map(self):
        floor_z = self.__get_floor_z()

        for surface in self.get_surfaces():
            points = surface.points

            normalized = [point[:2] + [point[2] - floor_z] for point in points]
            stringified = [" ".join(map(str, coords)) for coords in normalized]
            surface.raw_xml_element.text = " ".join(stringified)

    def __get_floor_z(self):
        building_points = []

        for surface in self.get_surfaces():
            for point in surface.points:
                building_points.append(point)

        return min(building_points, key=lambda x: x[2])[2]
