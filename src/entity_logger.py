import csv
from datetime import time
from os import path
from typing import List

from src.packet_entity import Packet_entity
from src.util import get_project_root


class Entity_Logger:
    def __init__(self, filename):
        self.__filepath = None
        self.filepath = filename

    def create_file(self):
        open(self.filepath, 'w+')

    @property
    def filepath(self):
        return self.__filepath + ".csv"

    @filepath.setter
    def filepath(self, filename):
        if self.__filepath is None:
            self.__filepath = path.join(get_project_root(), path.join('data', filename))

        duplicate_number = 0
        while path.isfile(self.filepath):
            duplicate_number += 1
            self.__filepath = path.join(get_project_root(), path.join('data', filename)) + "_({})".format(
                duplicate_number)

    def log(self, entities: List[Packet_entity]):
        if not path.isfile(self.filepath):
            self.create_file()

        with open(self.filepath, 'a', ) as file:
            writer = csv.writer(file)
            for entity in entities:
                writer.writerow([entity.id, entity.time])
