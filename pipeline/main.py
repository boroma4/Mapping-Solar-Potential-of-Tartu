from lib.solar_potential_pipeline import SolarPotentialPipeline
from lib.util.lod import Level

import argparse
import logging


def configure_logger():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler()
        ]
    )


def configure_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lod", help='level of detail, defaults to 2', default=2, type=int)
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
    parser.add_argument(
        "--roof-coverage",
        help="fraction of the roof that can be covered with solar panels, defaults to 0.90",
        type=float,
        default=0.90)
    parser.add_argument(
        "--optimize-2d-map",
        help="optimize the buildings to have the floor at z = 0",
        type=bool,
        default=True)
    parser.add_argument("--output-format", help="output type to convert CityGML files to (3Dtiles, ...)")
    parser.add_argument(
        "--node-ram-limit",
        help="Max amout of RAM in MB allowed to be used by Node.js, defaults to 5500",
        default=5500,
        type=int)

    return parser


if __name__ == "__main__":
    configure_logger()
    parser = configure_parser()
    args = parser.parse_args()

    specific_file_name = args.filename
    lod_num = args.lod
    pv_efficiency = args.pv_efficiency
    pv_loss = args.pv_loss
    roof_coverage = args.roof_coverage
    optimize_2d_map = args.optimize_2d_map
    output_format = args.output_format
    node_ram_limit = args.node_ram_limit

    logging.info('Inputs:')
    logging.info(f'==================================')
    logging.info(f'Filename: {specific_file_name}')
    logging.info(f'LOD: {lod_num}')
    logging.info(f'PV efficiency: {pv_efficiency}')
    logging.info(f'PV loss: {pv_loss}')
    logging.info(f'Roof coverage: {roof_coverage}')
    logging.info(f'Optimize for 2D map: {optimize_2d_map}')
    logging.info(f'Output format: {output_format}')
    logging.info(f'Node RAM limit: {node_ram_limit} MB')
    logging.info(f'==================================')

    lods = {
        1: Level.LOD1,
        2: Level.LOD2
    }

    if lod_num not in lods.keys():
        raise Exception("Unsupported LOD")

    SolarPotentialPipeline(
        specific_file_name,
        lods[lod_num],
        pv_efficiency,
        pv_loss,
        roof_coverage,
        optimize_2d_map,
        output_format,
        node_ram_limit
    ).run()
