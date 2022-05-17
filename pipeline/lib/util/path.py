import os
import glob

from argparse import ArgumentError
from lib.util.lod import Level

DATA_PATH = "data"


class PathUtil:
    def __init__(self, lod):
        self.__lod = lod

    def get_data_dir_path(self):
        if self.__lod == Level.LOD1:
            return os.path.join(DATA_PATH, 'lod1')
        elif self.__lod == Level.LOD2:
            return os.path.join(DATA_PATH, 'lod2')
        else:
            raise ArgumentError("Invalid LOD")

    def get_path_gml(self, id):
        if not id.endswith(".gml"):
            id += ".gml"
        return os.path.join(self.get_data_dir_path(), id)

    def get_path_json(self, id):
        if not id.endswith(".json"):
            id += ".json"
        return os.path.join(self.get_data_dir_path(), id)

    def get_js_script(self, name):
        return glob.glob(f"./**/node_scripts/{name}", recursive=True)[0]

    def get_tmp_dir_path(self):
        path = os.path.join(DATA_PATH, "tmp")
        if not os.path.isdir(path):
            os.mkdir(path)

        return path
