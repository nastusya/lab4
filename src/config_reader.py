from configparser import ConfigParser
import os


moduledir = os.path.abspath(os.path.dirname(__file__))
CONFIG_FILE = os.path.join("../config.ini")

cfg = ConfigParser()
cfg.read(CONFIG_FILE)
