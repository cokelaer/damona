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
#  website: https://github.com/damona/damona
#  documentation: http://damona.readthedocs.io
#
##############################################################################


import pathlib
import glob
import os
import yaml
from yaml import Loader
from damona import logger


class Registry():
    """

    The registry contains a dictionary with names of images and metadata
    information about them::

        r = Registry()
        r.registry
        r.registry['prokka_1.14.5']['download']

    """

    def __init__(self):
        self.registry = {}
        self.discovery()

    def _read_registry(self, registry):
        if os.path.exists(registry) is False:
            raise IOError("incorrect input filename {}".format(registry))

        # read the yaml
        data = yaml.load(open(registry, "r").read(), Loader=Loader)

        # some checks
        for k, v in data.items():
            if "class" not in v: 
                logger.warning("missing class in {}".format(registry))
            if "version" not in v:
                logger.warning("missing version in {}".format(registry))
            if "download" not in v:
                logger.warning("missing download in {}".format(registry))
            if data[k]["class"] == "exe":
                if "binaries" not in v:
                    logger.warning("missing binaries field in {}".format(registry))
        return data


    def discovery(self):
        from damona.recipes import __path__
        self._registry_files = glob.glob(__path__[0] + '/*/registry.yaml')
        self._singularity_files = glob.glob(__path__[0] + '/*/Singularity.*')

        self.registry = {}

        for registry in self._registry_files:
            data = self._read_registry(registry)
            for k, v in data.items():
                name = k.replace("Singularity.", "").lower()
                if name not in self.registry:
                    self.registry[name] = v
                else: #pragma: no cover
                    raise ValueError("found a duplicated name {}".format(name))

        for filename in self._singularity_files:
            p = pathlib.Path(filename)
            if (p.parent / "registry.yaml").exists() is False:
                logger.warning("Missing registry in {}. You may use 'damona registry {} to start with".format(p.parent, p.parent))

    def get_downloadable_link(self, name):
        pass

    def create_registry(self, path):
        #recipes = glob.glob(pathlib.Path(path).absolute() / "Singularity*")
        recipes = glob.glob(path +  "/Singularity*")
        for recipe in recipes:
            try:version = recipe.rsplit("_")[-1]
            except: version = "fillme"
            print("""{}:
    version: {}
    class: choose one in : exe, env,set
    download: library://path_to_image
    binaries: if env delete this file otherwise complete with list of binaries
        - name1 in singularity: name1 in your env
        - name1 in singularity: name1 in your env
    """.format(recipe.rsplit("/",1)[1], version))

    def get_list(self, pattern=None):

        from damona.recipes import __path__
        recipes = glob.glob(__path__[0] + '/*/Singularity.*')
        recipes = [os.path.basename(x) for x in recipes]
        recipes = [x.replace("Singularity.", "").lower() for x in recipes]
        recipes = [x.replace("_", ":").lower() for x in recipes]
        recipes = sorted(recipes)

        if pattern:
            recipes = [x for x in recipes if pattern in x]

        return recipes
