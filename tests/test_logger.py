from os import path, remove, listdir

from src import util
from src.data_logger import Data_Logger

log_file_name = 'test_log'


class Test_logger():
    def teardown_method(self):
        for file in listdir(path.join(util.get_project_root(), "data")):
            if log_file_name in file:
                remove(path.join(util.get_project_root(), "data", file))

    @staticmethod
    def get_absolute_log_file_path(extra=''):
        file_location = path.join('data', log_file_name + extra + '.csv')
        return path.join(util.get_project_root(), file_location)

    def test_filename_full_path_is_in_data_dir(self):
        logger = Data_Logger(log_file_name)
        absolute_path = self.get_absolute_log_file_path()

        assert absolute_path == logger.filepath

    def test_logger_should_create_file(self):
        # should create a log file
        logger = Data_Logger(log_file_name)  # NOQA - creates the object
        assert path.exists(self.get_absolute_log_file_path())

    def test_add_number_to_filename_if_file_exist(self):
        open(self.get_absolute_log_file_path(), 'w+')
        logger = Data_Logger(log_file_name)

        replacement_file_name = self.get_absolute_log_file_path("_(1)")
        assert replacement_file_name == logger.filepath

    def test_add_number_to_filename_if_two_file_exist(self):
        logger = Data_Logger(log_file_name)
        logger1 = Data_Logger(log_file_name)
        logger2 = Data_Logger(log_file_name)

        replacement_file_name = self.get_absolute_log_file_path("_(2)")
        assert replacement_file_name == logger2.filepath
