from os import path

from src.util import get_project_root


class Data_Logger:
	def __init__(self, filename):
		self.filepath = path.join(get_project_root(), path.join('data', filename))
		open(self.filepath, 'w+')

# def __exit__(self, exc_type, exc_val, exc_tb):
#	pass
