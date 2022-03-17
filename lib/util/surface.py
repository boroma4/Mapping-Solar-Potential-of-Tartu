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




    def is_roof(self, z_max, z_min) -> bool:
        lowest_z = min([z for _, _, z in self.points])
        _, tilt = self.angles()

        return lowest_z > (z_min + (z_max - z_min) / 2) and (tilt <= 60 or tilt >= 120)

    
    #area of polygon poly
    def area(self):
        return geometry.area(self.points)

        
    def angles(self):
        normal = geometry.get_normal(self.points)
        az, tilt = geometry.get_angles(normal)
        return az, tilt

