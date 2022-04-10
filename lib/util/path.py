from argparse import ArgumentError
import os
from lib.util.lod import Level
 
DATA_PATH = "data"

class PathUtil:
    def __init__(self, data_path, lod):
        self.data_path = data_path or DATA_PATH
        self.__lod = lod

    def get_data_dir_path(self):
        if self.__lod == Level.LOD1:
            return os.path.join(self.data_path, 'lod1')
        elif self.__lod == Level.LOD2:
            return os.path.join(self.data_path, 'lod2')
        else:
            raise ArgumentError("Invalid LOD")


    def get_path_gml(self, id):
        return os.path.join(self.get_data_dir_path(), f'{id}.gml')

    def get_path_json(self, id):
        return os.path.join(self.get_data_dir_path(), f'{id}.json')