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
