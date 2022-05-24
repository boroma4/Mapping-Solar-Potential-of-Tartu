from lib.util.xml_constants import *
from pyproj import Proj, transform
from pipeline.lib.citygml.surface import Surface


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
        first_surface_str = list(self.get_surfaces())[0].text
        x, y = list(map(float, first_surface_str.split(" ")[:2]))

        # TODO: make dynamic based on the file
        return transform(Proj('EPSG:3301'), Proj('EPSG:4326'), x, y)

    def optimize_for_2d_map(self):        
        floor_z = self.__get_floor_z()

        for xml_points in self.get_surfaces():
            points = []
            floats = [float(e) for e in xml_points.text.split(" ")]
            divisions = len(floats) // 3

            for i in range(divisions):
                points.append(floats[i * 3: (i + 1) * 3])

            normalized = [point[:2] + [point[2] - floor_z] for point in points]
            stringified = [" ".join(map(str, coords)) for coords in normalized]
            xml_points.text = " ".join(stringified)

    def __get_floor_z(self):
        points = []

        for xml_points in self.get_surfaces():
            floats = [float(e) for e in xml_points.text.split(" ")]
            divisions = len(floats) // 3
            for i in range(divisions):
                points.append(floats[i * 3: (i + 1) * 3])
        
        return min(points, key=lambda x: x[2])[2]