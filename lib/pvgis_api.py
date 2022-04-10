import logging
import requests

BASE_PVCALC_URL = "https://re.jrc.ec.europa.eu/api/v5_2/PVcalc"
MANDATORY_FIELDS = ["db", "mounting_place", "loss", "lat", "lon", "peak_power", "angle", "azimuth"]

class PvgisRequest:
    def __init__(self) -> None:
        self.db = "PVGIS-SARAH2"
        self.mounting_place = "building"
        self.output_format = "json"
        self.loss = 0.10
        self.optimal_angles = False

    def set_location(self, lon, lat):
        self.lon = lon
        self.lat = lat
        return self
    
    # Peak power of PV system in kW, to be calculated by roof area
    def set_peak_power_kw(self, peak_power):
        self.peak_power = peak_power
        return self

    def set_loss(self, loss):
        self.loss = loss
        return self
    
    def set_angle(self, angle):
        self.angle = angle
        return self
    
    def set_azimuth(self, azimuth):
        self.azimuth = azimuth
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
            "angle": float(self.angle),
            "aspect": float(self.azimuth),
            "outputformat": self.output_format,
            "raddatabase": self.db,
            "optimalangles": int(self.optimal_angles)
        }