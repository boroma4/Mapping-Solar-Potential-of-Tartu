import os

from lib.step import IStep
from google_drive_downloader import GoogleDriveDownloader as gdd
from lib.util.path import get_path_gml

class Loader(IStep):
    def __init__(self, file_gdrive_id):
        self.__file_gdrive_id = file_gdrive_id

    def execute(self):
        if self.__check_exists():
            print(f"File with id {self.__file_gdrive_id} found, skipping loading...")
            return
        self.__load()

    def cleanup(self):
        os.remove(get_path_gml(self.__file_gdrive_id))

    def __check_exists(self):
        return os.path.isfile(get_path_gml(self.__file_gdrive_id))
    
    def __load(self):
        gdd.download_file_from_google_drive(
            file_id=self.__file_gdrive_id,
            dest_path=get_path_gml(self.__file_gdrive_id), 
            unzip=True
        )

