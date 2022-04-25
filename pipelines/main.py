from lib.solar_potential_pipeline import SolarPotentialPipeline
from lib.util.lod import Level

import argparse
import logging
import os


def configure_logger():
    dir_name = "logs"

    if not os.path.exists(dir_name):
        os.mkdir(dir_name)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler()
        ]
    )


def configure_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("pipeline", help="tiles or solar")
    parser.add_argument("--lod", help='level of detail, defaults to 2', default=2, type=int)
    parser.add_argument("--datapath", help='path to CityGML files, defaults to ./data', default="data")
    parser.add_argument("--filename", help='specify if you want to run pipeline on a certain file')
    parser.add_argument(
        "--pv-efficiency",
        help="efficiency of the PV system, defaults to 0.20",
        type=float,
        default=0.20)
    parser.add_argument(
        "--pv-loss",
        help="losses in cables, power inverters, dirt, etc. defaults to 0.14",
        type=float,
        default=0.14)

    return parser


if __name__ == "__main__":
    configure_logger()
    parser = configure_parser()
    args = parser.parse_args()

    pipeline_type = args.pipeline.lower()
    data_path = args.datapath
    specific_file_name = args.filename
    lod_num = args.lod
    pv_efficiency = args.pv_efficiency
    pv_loss = args.pv_loss

    if pipeline_type not in ["solar", "tiles"]:
        raise Exception("Wrong pipeline type")
    if lod_num not in [1, 2]:
        raise Exception("Unsupported LOD")

    lod = Level.LOD1 if lod_num == 1 else Level.LOD2

    if pipeline_type == "solar":
        SolarPotentialPipeline(data_path, specific_file_name).run(lod, pv_efficiency, pv_loss)
