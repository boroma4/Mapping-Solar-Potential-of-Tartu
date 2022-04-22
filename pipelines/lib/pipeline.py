import os
import xml.etree.ElementTree as ET
import logging
import time

from lib.util.path import PathUtil
from lib.xml_constants import *

UPDATED_PREFIX = "updated-"


class Pipeline:
    def __init__(self, data_path, single_file_name=None) -> None:
        self.data_path = data_path
        self.single_file_name = single_file_name

    def process_files(self, level, processor):
        path_util = PathUtil(self.data_path, level)
        data_dir_path = path_util.get_data_dir_path()

        for filename in os.listdir(data_dir_path):
            # For running on only one file
            if self.single_file_name and self.single_file_name != filename:
                continue

            original_file_path = os.path.join(data_dir_path, filename)
            is_valid_prefix_and_suffix = original_file_path.endswith(
                ".gml") and not filename.startswith(UPDATED_PREFIX)

            if os.path.isfile(original_file_path) and is_valid_prefix_and_suffix:
                logging.info(f'Processing {filename}, level: {level}')
                start_time = time.time()

                tree = ET.parse(original_file_path)

                processor(tree, path_util, filename)

                end_time = time.time()
                duration = round(end_time - start_time, 3)

                logging.info(f"Done. Took {duration}s")
            else:
                logging.info(f'Ignoring file: {original_file_path}')

    def extract_id(self, string_id):
        subparts = string_id.split("_")
        return subparts[1]
