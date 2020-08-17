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
import sys

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
        # Do not change the print statement here below. They are used by
        # damona.sh
        if env_name not in self.environments:
            logger.error(f"invalid environment:  {env_name}. Please use 'damona env' to get the list")
            sys.exit(1)
        env_path = env_directory / env_name
        print('    export DAMONA_ENV={};'.format(env_path))
        print('export PATH={}/bin:${{PATH}}'.format(env_path))

    def deactivate(self):
        # Do not change the print statement here below. They are used by
        # damona.sh
        PATH = os.environ['PATH']
        paths = PATH.split(":")
        newPATH = ":".join([x for x in paths if "config/damona/" not in x])
        from damona import damona_config_path
        damona_config_path
        newPATH = damona_config_path+"/bin" + ":" +  newPATH
        print('    export DAMONA_ENV={};'.format(damona_config_path))
        print('export PATH={}'.format(newPATH))


    def create(self, env_name):
        env_path = env_directory / env_name
        if os.path.exists(env_path):
            logger.warning("{} exists already".format(env_path))
        else:
            try:
                os.mkdir(env_path)
                os.mkdir(env_path / "bin")
                logger.info("Created {} in {}".format(env_path, env_directory))
            except: #pragma: no cover
                logger.warning("Something went wrong. Could not create {}".format(env_path))

