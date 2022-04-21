import numpy as np
from lib.util import geometry


class Surface:
    def __init__(self, points_str: str) -> None:
        self.points: list[list[float]] = []
        self.__add_points(points_str)

    def __add_points(self, points_str: str) -> None:
        floats = [float(e) for e in points_str.split(" ")]
        divisions = len(floats) // 3
        for i in range(divisions):
            # add every 3 values
            current_points = floats[i * 3: (i + 1) * 3]
            if self.points and current_points == self.points[-1]:
                continue

            self.points.append((floats[i * 3: (i + 1) * 3]))

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
