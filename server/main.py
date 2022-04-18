from lib.pvgis_api import PvgisRequest
from lib.solar import calculate_peak_power_kpw, calculate_usable_area
from flask import Flask, request
from init import load_building_db, configure_logger


app = Flask(__name__)
data = load_building_db()


@app.route('/')
def hello():
    return 'Hello, World!'


@app.route('/solar', methods=["GET"])
def solar():
    args = request.args
    building_id = args.get("etak_id")

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
    return {"pv": pv_calculations} | {"building": building_data}


if __name__ == "__main__":
    app.run('0.0.0.0', '8000', debug=True)
