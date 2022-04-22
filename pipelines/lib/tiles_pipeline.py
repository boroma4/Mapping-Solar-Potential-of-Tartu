import os
import xml.etree.ElementTree as ET
import logging

from lib.xml_constants import *
from lib.pipeline import Pipeline, UPDATED_PREFIX


class TilesPipeline(Pipeline):
    def run(self, level):
        logging.info("Running Tiles pipeline")
        self.process_files(level, self.process)

    def process(self, tree, path_util, filename):
        data_dir_path = path_util.get_data_dir_path()
        buildings = tree.getroot().findall(f"{CORE}cityObjectMember")
        self.__process_buildings(buildings)

        processed_file_path = os.path.join(
            data_dir_path, f"{UPDATED_PREFIX}{filename}")

        logging.info("Updating XML tree")
        tree.write(processed_file_path)

        logging.info("Converting CityGML to 3D tiles")

        tiles_dir_path = processed_file_path.removesuffix(".gml")
        if not os.path.exists(tiles_dir_path):
            os.mkdir(tiles_dir_path)

        os.system(f"NODE_OPTIONS=--max-old-space-size=10000 citygml-to-3dtiles {processed_file_path} {tiles_dir_path}/")

    def __process_buildings(self, buildings):
        count_total = len(buildings)
        count_processed = 0

        for xml_building in buildings:
            id = self.extract_id(xml_building[0].attrib[ID])
            self.__update_tree(xml_building, id)

            count_processed += 1
            if count_processed % 5000 == 0:
                logging.info(f"Processed {count_processed} / {count_total} buildings")

    def __update_tree(self, xml_building, id):
        gen = "ns3"
        id_tag = ET.SubElement(xml_building[0], f'{gen}:stringAttribute')
        id_tag.attrib["name"] = "str_id"
        id_tag_value = ET.SubElement(id_tag, f'{gen}:value')
        id_tag_value.text = id
