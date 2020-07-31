import pkg_resources
import os
import pathlib

try:
    version = pkg_resources.require("damona")[0].version
except:
    version = ">=0.8.3"


import colorlog
logger = colorlog.getLogger("damona")

from easydev import CustomConfig
configuration = CustomConfig("damona", verbose=True)
damona_config_path = configuration.user_config_dir



path = pathlib.Path(damona_config_path)
bin_directory = path / 'bin'
images_directory = path / 'images'

try:
    bin_directory.mkdir()
except:
    pass # exists already

try:
    images_directory.mkdir()
except:
    pass # exists already
