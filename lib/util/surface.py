import numpy as np


class Surface:
    def __init__(self, points_str: str) -> None:
        self.points: list[list[float]] = []
        self.__add_points(points_str)

        
    def __add_points(self, points_str: str) -> None:
        floats = [float(e) for e in points_str.split(" ")]
        divisions = len(floats) // 3

        for i in range(divisions):
            # add every 3 values
            self.points.append((floats[i * 3: (i + 1) * 3]))


    def is_lod1_roof(self, roof_height) -> bool:
        is_roof = True
        for point in self.points:
            z = point[2]
            if z != roof_height:
                is_roof = False
                break
        
        return is_roof
    

    def is_lod2_roof(self, roof_height) -> bool:
        return True

    # https://stackoverflow.com/questions/12642256/find-area-of-polygon-from-xyz-coordinates
    def area(self):
        poly = np.array(self.points)
        #all edges
        edges = poly[1:] - poly[0:1]
        # row wise cross product
        cross_product = np.cross(edges[:-1],edges[1:], axis=1)
        #area of all triangles
        area = np.linalg.norm(cross_product, axis=1) / 2
        return sum(area)

    def incline(self):
        return 0.0
