from lib.pvgis_api import PvgisRequest
from lib.solar import calculate_peak_power_kpw, calculate_usable_area
from flask import Flask, request

import logging
import os
import datetime
import json

# JSON for now
def load_building_db():
    with open("./data/lod2/tartu.json") as f:
        return json.load(f)


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


app = Flask(__name__)
data = load_building_db()


@app.route('/')
def hello():
    return 'Hello, World!'


@app.route('/solar', methods=["GET"])
def solar():
    args = request.args
    building_id = args.get("id")

    if not building_id or building_id not in data:
        return "Invalid building ID specified", 400

    efficiency = args.get(
        "efficiency",
        default=0.20,
        type=float)  # efficiency of the PV system

    building_data = data[building_id]
    latitude = building_data["lat"]
    longitude = building_data["lon"]
    roof_area = building_data["total_roof_area"]  # m2

    usable_area = calculate_usable_area(roof_area)
    kpw = calculate_peak_power_kpw(usable_area, efficiency)

    pv_calculations = PvgisRequest() \
        .set_location(longitude, latitude) \
        .set_peak_power_kwp(kpw) \
        .set_mounting_place("building") \
        .optimize_angles() \
        .send()

    # merge dictionaries
    return {"pv" : pv_calculations} | {"building": building_data}


if __name__ == "__main__":
    app.run('0.0.0.0', '8000', debug=True)
