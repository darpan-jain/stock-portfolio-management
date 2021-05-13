from utils.logging_setup import setup_logger
import configparser
import os

if not os.path.exists('logs'):
	os.mkdir('logs')

app = setup_logger('app', './logs/app.log')
thanos = setup_logger('thanos', './logs/thanos.log')


def read_cfg():
	config = configparser.ConfigParser()
	config.read('utils/configs/config.ini')
	return config
