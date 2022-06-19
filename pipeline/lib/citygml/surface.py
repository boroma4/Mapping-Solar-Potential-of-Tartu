from xml.etree.ElementTree import Element
from lib.util import geometry
from lib.util.constants import *


class Surface:
    def __init__(self, xml_element: Element) -> None:
        self.points: list[list[float]] = []
        self.raw_xml_element = xml_element
        self.__add_points(xml_element)
        self.normal = geometry.get_normal(self.points)
        self.azimuth, self.tilt = geometry.get_angles(self.normal)
        self.orientation = self.__get_orientation()
        self.area = geometry.area(self.points)

    def __add_points(self, linear_ring_element: Element) -> None:
        floats = [float(e) for e in linear_ring_element.text.split(" ")]
        divisions = len(floats) // 3
        for i in range(divisions):
            # add every 3 values
            current_points = floats[i * 3: (i + 1) * 3]
            if self.points and current_points == self.points[-1]:
                continue

            self.points.append(current_points)

    def is_roof(self, z_min: float) -> bool:
        is_tilted = self.tilt <= 60
        is_floor = all([point[2] == z_min for point in self.points])

        return is_tilted and not is_floor

    def angles(self):
        return self.tilt, self.azimuth

    def __get_orientation(self):
        if self.tilt <= MAX_FLAT_SURFACE_TILT:
            return NONE
        if -45 <= self.azimuth <= 45:
            return SOUTH
        if -135 <= self.azimuth <= 45:
            return EAST
        if 45 <= self.azimuth <= 135:
            return WEST
        return NORTH
