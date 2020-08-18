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
from damona import damona_config_path
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
            path = damona_config_path
        else:
            path = os.environ['DAMONA_ENV']
        return path

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

    def activate(self, env_name=None):
        #self.deactivate()
        # Do not change the print statement here below. They are used by
        # damona.sh
        if env_name not in self.environments + ['base']:
            logger.error(f"invalid environment:  {env_name}. Please use 'damona env' to get the list")
            sys.exit(1)
        if env_name == "base":
            env_path = env_directory.parent 
            print('    export DAMONA_ENV={};'.format(env_path))
            print('export PATH={}/bin:${{PATH}}'.format(env_path))
        else:
            env_path = env_directory / env_name
            print('    export DAMONA_ENV={};'.format(env_path))
            print('export PATH={}/bin:${{PATH}}'.format(env_path))

    def deactivate(self):
        # we deactivate the latest activated environment only.
        # can be called several times. If called too many times,
        # we set the main damona environment (base) as default
        PATH = os.environ['PATH']
        paths = PATH.split(":")


        first_found = False   # this one is the one to deactivate (to ignore)
        found_damona_path = None # this one is the next one
        newPATH = []
        for path in paths:
            if "config/damona" in path:
                # we skip the first one.
                if first_found is False:
                    first_found = True
                else: # keep track of the DAMONA_ENV.
                    newPATH.append(path)
                    if found_damona_path is None:
                        found_damona_path = path
            else: # in all other cases, we keep the path.
                newPATH.append(path)

        #
        newPATH = ":".join(newPATH)
        if found_damona_path:
            print('    export DAMONA_ENV={};'.format(found_damona_path.rsplit('/bin')[0])) 
        else:
            newPATH = damona_config_path + ":" + newPATH
            print('    export DAMONA_ENV={};'.format(damona_config_path))
        print('export PATH={}'.format(newPATH))

    def create(self, env_name):
        if env_name == "base":
            logger.critical("base is a reserved name for environement. Cannot be created")
            sys.exit(1)
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

