import os
import json
import logging


def write_json(dictionary, dir_path, filename):
    json_path = os.path.join(dir_path, filename)

    with open(json_path, 'w') as fp:
        json.dump(dictionary, fp)

    json_file_size_mb = get_file_size_mb(json_path)
    logging.info(f"{filename} is {json_file_size_mb} MB")

def read_json(dir_path, filename):
    json_path = os.path.join(dir_path, filename)
    json_file_size_mb = get_file_size_mb(json_path)
    logging.info(f"Reading JSON, {filename} is {json_file_size_mb} MB")

    with open(json_path, 'r') as fp:
        return json.loads(fp.read())

def get_file_size_mb(path):
    return round(os.path.getsize(path) / 2 ** 20, 3)
