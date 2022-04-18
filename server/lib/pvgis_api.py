import logging
import requests

BASE_PVCALC_URL = "https://re.jrc.ec.europa.eu/api/v5_2/PVcalc"
MANDATORY_FIELDS = [
    "db",
    "mounting_place",
    "loss",
    "lat",
    "lon",
    "peak_power",
    "optimal_angles"
]


class PvgisRequest:
    def __init__(self) -> None:
        self.db = "PVGIS-SARAH2"
        self.mounting_place = "building"
        self.output_format = "json"
        self.loss = 0.14
        self.optimal_angles = False

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

    def send(self):
        logging.info("Sending a request to PVgis")
        self.validate_fields()
        payload = self.__build_payload()
        resp = requests.get(BASE_PVCALC_URL, params=payload)

        if not resp.ok:
            raise Exception(f"Reuqest failed with code {resp.status_code}")

        output = resp.json()["outputs"]
        return output

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
            # "angle": float(getattr(self, "angle")),
            # "aspect": float(getattr(self, "azimuth")),
            "outputformat": self.output_format,
            "raddatabase": self.db,
            "optimalangles": int(self.optimal_angles)
        }


# variables:
# 'E_d': {'description': 'Average daily energy production from the given system', 'units': 'kWh/d'},
# 'E_m': {'description': 'Average monthly energy production from the given system', 'units': 'kWh/mo'},
# 'E_y': {'description': 'Average annual energy production from the given system', 'units': 'kWh/y'},
# 'H(i)_d': {'description': 'Average daily sum of global irradiation per square meter received by the modules of the given system', 'units': 'kWh/m2/d'},
# 'H(i)_m': {'description': 'Average monthly sum of global irradiation per square meter received by the modules of the given system', 'units': 'kWh/m2/mo'},
# 'H(i)_y': {'description': 'Average annual sum of global irradiation per square meter received by the modules of the given system', 'units': 'kWh/m2/y'},
# 'SD_m': {'description': 'Standard deviation of the monthly energy production due to year-to-year variation', 'units': 'kWh'},
# 'SD_y': {'description': 'Standard deviation of the annual energy production due to year-to-year variation', 'units': 'kWh'},
# 'l_aoi': {'description': 'Angle of incidence loss', 'units': '%'},
# 'l_spec': {'description': 'Spectral loss', 'units': '%'},
# 'l_tg': {'description': 'Temperature and irradiance loss', 'units': '%'},
# 'l_total': {'description': 'Total loss', 'units': '%'}
