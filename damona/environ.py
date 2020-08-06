# -*- coding: utf-8 -*-
#
#  This file is part of Damona software
#
#  Copyright (c) 2016 - Damona Development Team
#
#  File author(s):
#      Thomas Cokelaer <thomas.cokelaer@pasteur.fr>
#
#  Distributed under the terms of the 3-clause BSD license.
#  The full license is in the LICENSE file, distributed with this software.
#
#  website: https://github.com/cokelaer/damona
#  documentation: http://damona.readthedocs.io
#
##############################################################################
from damona import env_directory
import os
import shutil
from damona import logger


class Environ():
    def __init__(self):
        pass

    @staticmethod
    def get_current_env():
        if 'DAMONA_ENV' not in os.environ:
            from damona import damona_config_path
            return damona_config_path
        else:
            return os.environ['DAMONA_ENV'] 
    
    def _get_N(self):
        return len(self.environments)
    N = property(_get_N)

    def _get_envs(self):
        envs = os.listdir(str(env_directory))
        return envs
    environments = property(_get_envs)

    def delete(self, env_name):
        env_path = env_directory / env_name
        if os.path.exists(env_path) is False:
            logger.error("{} does not exists".format(env_path))
        else:
            try:
                os.rmdir(env_path)
            except OSError:
                logger.warning("Will delete all contents of {}. Although this concerns only aliases you will lose your environement".format(env_path))
                ret = input("Are you sure you want to proceed ? (N/y)")
                if ret == 'y':
                    shutil.rmtree(env_path)

    def activate(self, env_name):
        assert env_name in self.environments, "invalid name. use 'damona env' to get the list"
        env_path = env_directory / env_name
        # this cannot be done permanently from python
        print("This feature is not fully implemented yet. Please set the environmental "
              " variable manually. For information about environmental variable, see "
               "e.g. https://www.schrodinger.com/kb/1842")
        print("Under bash type:\n")
        print('    export DAMONA_ENV="{}"\n'.format(env_path))

    def create(self, env_name):
        env_path = env_directory / env_name
        if os.path.exists(env_path):
            logger.warning("{} exists already".format(env_path))
        else:
            try:
                os.mkdir(env_path)
                os.mkdir(env_path / "bin")
                logger.info("Created {} in {}".format(env_path, env_directory))
            except:
                logger.warning("Something went wrong. Could not create {}".format(env_path))

