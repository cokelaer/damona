import pkg_resources
import os
import pathlib

try:
    version = pkg_resources.require("damona")[0].version
except:   #pragma: no cover
    version = ">=0.8.3"


import colorlog

handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
	'%(log_color)s%(levelname)s:%(name)s: %(message)s'))
logger = colorlog.getLogger("damona")
logger.addHandler(handler)

from easydev import CustomConfig
configuration = CustomConfig("damona", verbose=True)
damona_config_path = configuration.user_config_dir



path = pathlib.Path(damona_config_path)
bin_directory = path / 'bin'
images_directory = path / 'images'

try:
    bin_directory.mkdir()
except: # pragma: no cover
    pass # exists already

try:
    images_directory.mkdir()
except: #pragma: no cover
    pass # exists already

from damona.registry import Registry
