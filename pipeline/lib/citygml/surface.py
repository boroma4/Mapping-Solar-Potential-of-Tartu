import numpy as np
from lib.util import geometry


class Surface:
    def __init__(self, xml_element) -> None:
        self.points: list[list[float]] = []
        self.raw_xml_element = xml_element
        self.__add_points(xml_element)

    def __add_points(self, linear_ring_element) -> None:
        floats = [float(e) for e in linear_ring_element.text.split(" ")]
        divisions = len(floats) // 3
        for i in range(divisions):
            # add every 3 values
            current_points = floats[i * 3: (i + 1) * 3]
            if self.points and current_points == self.points[-1]:
                continue

            self.points.append(current_points)

    def is_roof(self, z_min) -> bool:
        _, tilt = self.angles()

        is_tilted = tilt <= 60
        is_floor = all([point[2] == z_min for point in self.points])

        return is_tilted and not is_floor

    def area(self):
        return geometry.area(self.points)

    def angles(self):
        normal = geometry.get_normal(self.points)
        az, tilt = geometry.get_angles(normal)
        return az, tilt
