import os


def get_file_size_mb(path):
    return round(os.path.getsize(path) / 2 ** 20, 3)
