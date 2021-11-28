from shapely.geometry import Polygon

class Surface:
    def __init__(self, points_str: str) -> None:
        self.points: list[Point] = []
        self.__add_points(points_str)

        
    def __add_points(self, points_str: str) -> None:
        floats = [float(e) for e in points_str.split(" ")]
        divisions = len(floats) // 3

        for i in range(divisions):
            # add every 3 values
            self.points.append(Point(floats[i * 3: (i + 1) * 3]))


    def is_roof(self, roof_height) -> bool:
        self.is_roof = True
        for point in self.points:
            if point.z != roof_height:
                self.is_roof = False
                break
        
        return self.is_roof

    
    def area(self) -> float:
        x = [p.x for p in self.points]
        y = [p.y for p in self.points]
        return Polygon(zip(x, y)).area



class Point: 
    def __init__(self, values: list[float]) -> None:
        [x, y, z] = values
        self.x = x
        self.y = y
        self.z = z