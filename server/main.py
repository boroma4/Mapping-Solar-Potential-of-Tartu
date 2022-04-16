from lib.pvgis_api import PvgisRequest
from lib.solar import calculate_peak_power_kpw, calculate_usable_area
from flask import Flask, request

import logging
import os
import datetime

app = Flask(__name__)

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

@app.route('/')
def hello():
    return 'Hello, World!'


@app.route('/solar', methods=["GET"])
def solar():
    args = request.args

    building_id = args.get("id")
    efficiency = args.get("efficiency", default=0.20, type=float) # efficiency of the PV system

    # to get from preprocessed data
    latitude = 58.3780
    longitude = 26.7290
    roof_area = 500  # m2

    usable_area = calculate_usable_area(roof_area)
    kpw = calculate_peak_power_kpw(usable_area, efficiency)

    res = PvgisRequest() \
        .set_location(longitude, latitude) \
        .set_angle(45) \
        .set_azimuth(0) \
        .set_peak_power_kwp(kpw) \
        .set_mounting_place("building") \
        .optimize_angles() \
        .send()
    
    return res

if __name__ == "__main__":
    app.run('0.0.0.0', '8000', debug=True)

