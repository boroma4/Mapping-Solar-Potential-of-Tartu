BASE_PVCALC_URL = "https://re.jrc.ec.europa.eu/api/v5_2/PVcalc"
MANDATORY_FIELDS = [
    "db",
    "mounting_place",
    "loss",
    "lat",
    "lon",
    "peak_power",
    "optimal_angles",
    "angle",
    "azimuth"
]


class PvgisRequestBuilder:
    def __init__(self) -> None:
        self.db = "PVGIS-SARAH2"
        self.mounting_place = "building"
        self.output_format = "json"
        self.loss = 0.14
        self.optimal_angles = False
        self.angle = 0
        self.azimuth = 0

    def set_location(self, lon, lat):
        self.lon = lon
        self.lat = lat
        return self

    def set_peak_power_kwp(self, peak_power):
        self.peak_power = peak_power
        return self

    # Losses in cables, power inverters, dirt (sometimes snow) on the modules
    # and so on
    def set_loss(self, loss):
        self.loss = loss
        return self

    def set_angle(self, angle):
        self.angle = angle
        return self

    def set_azimuth(self, azimuth):
        self.azimuth = azimuth
        return self

    def set_mounting_place(self, mounting_place):
        if mounting_place not in ["free", "building"]:
            raise Exception("Wrong mounting place value")

        self.mounting_place = mounting_place
        return self

    def optimize_angles(self):
        self.optimal_angles = True
        return self

    def get_payload(self):
        self.validate_fields()
        return self.__build_payload()

    def validate_fields(self):
        for field in MANDATORY_FIELDS:
            if getattr(self, field) is None:
                raise Exception(f"{field} is missing")

    def __build_payload(self):
        return {
            "lat": float(self.lat),
            "lon": float(self.lon),
            "peakpower": float(self.peak_power),
            "loss": float(self.loss),
            "mountingplace": self.mounting_place,
            "angle": float(self.angle),
            "aspect": float(self.azimuth),
            "outputformat": self.output_format,
            "raddatabase": self.db,
            "optimalangles": int(self.optimal_angles)
        }


def make_empty_response():
    response = {"totals": {"fixed": {"E_y": 0, "E_m_exact": []}}, "monthly": {"fixed": []}, "orientation": "north", "roofId": -1}
    for _ in range(12):
        response["totals"]["fixed"]["E_m_exact"].append(0)
        response["monthly"]["fixed"].append({"E_m": 0})

    return response
