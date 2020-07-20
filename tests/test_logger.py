from os import path as file
import mock

from src import util
from src.data_logger import Data_Logger

log_file_name = 'test_log.csv'


class Test_logger():

	def get_abselute_log_file_path(self):
		file_location = file.join('data', log_file_name)
		return file.join(util.get_project_root(), file_location)

	def test_logger_should_create_file(self):
		open_mock = mock.mock_open()
		# should create a log file
		logger = Data_Logger(log_file_name)

		assert file.exists(self.get_abselute_log_file_path())

	def test_filename_full_path_is_in_data_dir(self):
		logger = Data_Logger(log_file_name)

		absolute_path = self.get_abselute_log_file_path()

		assert absolute_path == logger.filepath
