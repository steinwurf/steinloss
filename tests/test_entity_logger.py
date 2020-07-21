from datetime import time
from os import path, remove, listdir
from unittest import mock

from src import util
from src.entity_logger import Entity_Logger
from src.packet_entity import Packet_entity

log_file_name = 'test_log'


class Test_logger():

    def setup_method(self):
        self.logger = Entity_Logger(log_file_name)

    def teardown_method(self):
        for file in listdir(path.join(util.get_project_root(), "data")):
            if log_file_name in file:
                remove(path.join(util.get_project_root(), "data", file))

    @staticmethod
    def get_absolute_log_file_path(extra=''):
        file_location = path.join('data', log_file_name + extra + '.csv')
        return path.join(util.get_project_root(), file_location)

    def test_filename_full_path_is_in_data_dir(self):
        absolute_path = self.get_absolute_log_file_path()

        assert absolute_path == self.logger.filepath

    def test_logger_should_create_file(self):
        assert path.exists(self.get_absolute_log_file_path())

    def test_add_number_to_filename_if_file_exist(self):
        # second logger after the teardown
        logger = Entity_Logger(log_file_name)

        replacement_file_name = self.get_absolute_log_file_path("_(1)")
        assert replacement_file_name == logger.filepath

    def test_add_number_to_filename_if_two_file_exist(self):
        logger1 = Entity_Logger(log_file_name)  # NOQA: the object only servese the purpose of making a file
        logger2 = Entity_Logger(log_file_name)

        replacement_file_name = self.get_absolute_log_file_path("_(2)")
        assert replacement_file_name == logger2.filepath

    def test_should_format_entity_as_id_time(self):
        entity = Packet_entity(2, time(hour=11, minute=35, second=45))
        mock_file = mock.mock_open()
        with mock.patch('src.entity_logger.open', mock_file, create=True) as mocked_file:
            self.logger.log(entity)
            output = mocked_file()
            output.write.assert_called_once_with('2,11:35:45\r\n')
