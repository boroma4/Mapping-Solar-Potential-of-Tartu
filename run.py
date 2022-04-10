from lib.preprocessor import Preprocessor
from lib.pvgis_api import PvgisRequest
from lib.solar import calculate_peak_power_kpw, calculate_usable_area
from datetime import datetime

import argparse
import logging
import os


def configure_logger():
    dir_name = "logs"

    if not os.path.exists(dir_name):
        os.mkdir(dir_name)

    logs_path = os.path.join(dir_name, str(datetime.now()))

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(logs_path),
            logging.StreamHandler()
        ]
    )


def configure_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--datapath")

    return parser


if __name__ == "__main__":
    configure_logger()
    parser = configure_parser()
    args = parser.parse_args()
    data_path = args.datapath

    preprocessor = Preprocessor(data_path)
    # preprocessor.process(Level.LOD1)
    # preprocessor.process(Level.LOD2)

    latitude = 58.3780
    longitude = 26.7290

    # will be inputs
    roof_area = 500  # m2
    efficiency = 0.20  # efficiency of the PV system

    usable_area = calculate_usable_area(roof_area)
    kpw = calculate_peak_power_kpw(usable_area, efficiency)

    res = PvgisRequest() \
        .set_location(longitude, latitude) \
        .set_angle(45) \
        .set_azimuth(0) \
        .set_peak_power_kwp(kpw) \
        .optimize_angles() \
        .send()

    logging.info(res)
