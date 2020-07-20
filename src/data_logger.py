from os import path

from src.util import get_project_root


class Data_Logger:
    def __init__(self, filename):
        self.filepath = self.generate_filepath_from_filename(filename)
        self.create_file(filename)

    def generate_filepath_from_filename(self, filename):
        return path.join(get_project_root(), path.join('data', filename))

    def create_file(self, filename):
        duplicate_number = 1
        while path.isfile(self.filepath):
            self.filepath = self.generate_filepath_from_filename(filename) + "_({})".format(duplicate_number)
            duplicate_number += 1
        open(self.filepath, 'w+')

    @property
    def filepath(self):
        return self.__filepath + ".csv"

    @filepath.setter
    def filepath(self, x):
        self.__filepath = x
