# https://stackoverflow.com/questions/12642256/find-area-of-polygon-from-xyz-coordinates
# https://github.com/tudelft3d/Solar3Dcity/blob/master/polygon3dmodule.py
import math
import numpy as np

# unit normal vector of plane defined by points a, b, and c


def unit_normal(a, b, c):
    x = np.linalg.det([[1, a[1], a[2]],
                       [1, b[1], b[2]],
                       [1, c[1], c[2]]])
    y = np.linalg.det([[a[0], 1, a[2]],
                       [b[0], 1, b[2]],
                       [c[0], 1, c[2]]])
    z = np.linalg.det([[a[0], a[1], 1],
                       [b[0], b[1], 1],
                       [c[0], c[1], 1]])
    magnitude = (x**2 + y**2 + z**2)**.5
    return (x / magnitude, y / magnitude, z / magnitude)

# area of polygon poly


def area(poly):
    if len(poly) < 3:  # not a plane - no area
        return 0
    total = [0, 0, 0]
    N = len(poly)
    for i in range(N):
        vi1 = poly[i]
        vi2 = poly[(i + 1) % N]
        prod = np.cross(vi1, vi2)
        total[0] += prod[0]
        total[1] += prod[1]
        total[2] += prod[2]
    result = np.dot(total, unit_normal(poly[0], poly[1], poly[2]))
    return abs(result / 2)


def get_angles(normal):
    """Get the azimuth and altitude from the normal vector."""
    # -- Convert from polar system to azimuth
    azimuth = 90 - math.degrees(math.atan2(normal[1], normal[0]))
    if azimuth >= 360.0:
        azimuth -= 360.0
    elif azimuth < 0.0:
        azimuth += 360.0

    # Azimuth is [0, 360], 0 is North direction, East is 90, West is -90
    # Converting to [-180, 180], 0 is South direction to be compatible with PVGIS API, East must be -90, West 90
    azimuth -= 180

    #[0, 90]
    t = math.sqrt(normal[0]**2 + normal[1]**2)
    if t == 0:
        tilt = 0.0
    else:
        # 0 for flat roof, 90 for wall
        tilt = 90 - abs(math.degrees(math.atan(normal[2] / t)))
    tilt = round(tilt, 3)

    return azimuth, tilt


def get_normal(polypoints):
    """Get the normal of the first three points of a polygon. Assumes planarity."""
    return unit_normal(polypoints[0], polypoints[1], polypoints[2])
