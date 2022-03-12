from datetime import date
from lib.util.lod import Level
from lib.preprocessor import Preprocessor
from datetime import datetime

import argparse
import logging
import os

def configure_logger():
    dir_name = "logs"

    if not os.path.exists(dir_name):
        os.mkdir(dir_name)
    
    logs_path = os.path.join(dir_name, str(datetime.now()))
    logging.basicConfig(level=logging.INFO)


def configure_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--goose")

    return parser

if __name__ == "__main__":
    configure_logger()
    parser = configure_parser()
    args = parser.parse_args()

    logging.info("Preprocessing .gml files\n")
    preprocessor = Preprocessor()
    preprocessor.process(Level.LOD1)
    preprocessor.process(Level.LOD2)

