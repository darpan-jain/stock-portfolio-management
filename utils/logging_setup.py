import configparser
import logging
from logging.handlers import RotatingFileHandler

class TracebackFilter(logging.Formatter):
	def format(self, record):
		record.exc_text = ''
		return super(TracebackFilter, self).format(record)

	def formatException(self, record):
		return ''

def read_cfg():
	config = configparser.ConfigParser()
	config.read('utils/configs/config.ini')
	return config

def setup_logger(logname, filename):
	"""
	The basic configuration for logging of the application

	Parameters
	----------

	name : str
		Name of the logger object, usually will be train/test

	filename : str
		Name and location of the logging file

	request_id : str
		Unique request ID for a particular asset

	Returns
	-------

	logger : logging object
		The logger object created with the specified configuration.

	"""

	log_format = '<%(asctime)s> [%(levelname)s] <%(lineno)s> <%(funcName)s> %(message)s'
	file_logger = RotatingFileHandler(filename, mode='a', maxBytes=500 * 1024 * 1024, backupCount=10)
	formatter = logging.Formatter(log_format, datefmt='%m/%d/%Y %I:%M:%S %p')
	file_logger.setFormatter(formatter)

	logger = logging.getLogger(logname)
	logger.setLevel(logging.DEBUG)
	logger.addHandler(file_logger)

	consoleHandler = logging.StreamHandler()
	consoleHandler.setFormatter(formatter)
	# consoleHandler.setFormatter(TracebackFilter(log_format, datefmt='%m/%d/%Y %I:%M:%S %p'))
	consoleHandler.setLevel(logging.DEBUG)
	# if read_cfg().getboolean('PARAMETERS', 'stream handler'):
		# logger.addHandler(consoleHandler)
	return logger
