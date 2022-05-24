import os
import xml.etree.ElementTree as ET
import logging
import time
import datetime

from lib.util.path import PathUtil
from lib.util.xml_constants import *

UPDATED_PREFIX = "updated-"


class Pipeline:
    def __init__(self, single_file_name=None) -> None:
        self.single_file_name = single_file_name

    def process_files(self, level, processor):
        path_util = PathUtil(level)
        data_dir_path = path_util.get_data_dir_path()

        for filename in os.listdir(data_dir_path):
            is_allowed_filename = not self.single_file_name or self.single_file_name == filename
            original_file_path = os.path.join(data_dir_path, filename)
            is_file = os.path.isfile(original_file_path)
            is_valid_prefix_and_suffix = original_file_path.endswith(
                ".gml") and not filename.startswith(UPDATED_PREFIX)

            if is_file and is_valid_prefix_and_suffix and is_allowed_filename:
                logging.info(f'Processing {filename}, level: {level}')
                start_time = time.time()

                tree = ET.parse(original_file_path)

                processor(tree, path_util, filename)

                end_time = time.time()
                duration_s = round(end_time - start_time, 3)

                logging.info(f"Done. Took {datetime.timedelta(seconds=duration_s)}")
            else:
                logging.info(f'Ignoring file: {original_file_path}')
