import json
import logging

from lib.surface import Surface
from lib.building import Building
from lib.xml_constants import *
from lib.pipeline import Pipeline


class SolarPotentialPipeline(Pipeline):
    def run(self, level):
        logging.info("Running Solar Potential pipeline")
        self.process_files(level, self.process)

    def process(self, tree, path_util, filename):
        buildings = tree.getroot().findall(f"{CORE}cityObjectMember")
        attribute_map = self.__process_buildings(buildings)

        logging.info("Wrtiting to JSON")
        json_name = filename.replace(".gml", "")

        with open(path_util.get_path_json(json_name), 'w') as fp:
            json.dump(attribute_map, fp)

    def __process_buildings(self, buildings):
        count_total = len(buildings)
        count_processed = 0
        count_no_roofs = 0
        attribute_map = {}

        for xml_building in buildings:
            id = self.extract_id(xml_building[0].attrib[ID])
            building = Building(id, xml_building)
            attribute_map[id] = attribute_map.get(id, {})
            z_min = building.get_z_min()

            # https://epsg.io/3301, unit - meters
            for points in building.get_surface_points():
                surface = Surface(points.text)

                if surface.is_roof(z_min):
                    area = surface.area()
                    azimuth, tilt = surface.angles()

                    attribute_map[id]["roofs"] = attribute_map[id].get("roofs", [])
                    roof_attribs = {"area": area, "azimuth": azimuth, "tilt": tilt}

                    if roof_attribs not in attribute_map[id]["roofs"]:
                        attribute_map[id]["roofs"].append(roof_attribs)

            if "roofs" not in attribute_map[id]:
                count_no_roofs += 1
                attribute_map[id]["roofs"] = [{"area": 0, "azimuth": 0, "tilt": 0}]

            total_roof_area = sum([roof["area"] for roof in attribute_map[id]["roofs"]])
            attribute_map[id]["total_roof_area"] = total_roof_area

            count_processed += 1
            if count_processed % 5000 == 0:
                logging.info(f"Processed {count_processed}/{count_total} buildings")

        logging.info(
            f"Roofs not detected for {count_no_roofs}/{count_total} buildings")

        return attribute_map
