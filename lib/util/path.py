import os

DATA_PATH = "data"

def get_path_gml(id):
    return os.path.join(DATA_PATH, f'{id}.gml')

def get_path_json(id):
    return os.path.join(DATA_PATH, f'{id}.json')