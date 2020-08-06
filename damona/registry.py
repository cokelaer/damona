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

    def __init__(self, from_url=None):
        if from_url == "damona":
            from_url = "https://biomics.pasteur.fr/drylab/damona/registry.txt"
        elif from_url:
            assert from_url.startswith('http')
            assert from_url.endswith('registry.txt')
        self.from_url = from_url
        self.registry = {}
        self.discovery()

    def _read_registry(self, registry):
        if os.path.exists(registry) is False: #pragma: no cover
            raise IOError("incorrect input filename {}".format(registry))

        # read the yaml
        data = yaml.load(open(registry, "r").read(), Loader=Loader)

        # some checks
        for k, v in data.items():
            if "class" not in v: #pragma: no cover
                logger.warning("missing class in {}".format(registry))
            if "version" not in v: #pragma: no cover
                logger.warning("missing version in {}".format(registry))
            if "download" not in v: #pragma: no cover
                logger.warning("missing download in {}".format(registry))
            if data[k]["class"] == "exe":
                if "binaries" not in v: #pragma: no cover
                    logger.warning("missing binaries field in {}".format(registry))
        return data

    def discovery(self):

        if self.from_url:
            self._url_discovery()
        else:
            self._local_discovery()

    def _url_discovery(self):
        self.registry = {}
        import  urllib.request

        response = urllib.request.urlopen(self.from_url)
        html = response.read()
        html = html.decode('utf-8')
        _class = None
        for registry in html.split("\n"):
            if registry.startswith("["):
                _class = registry.replace('[', '').replace(']','')
                continue
            if registry.strip() == "":
                continue
            else:
                data = {}
                name,version = registry.split("_")
                version = version.rsplit(".", 1)[0]
                # todo for now only exe fills the binaries assuming name of
                # package is the name of the binary
                self.registry[name+"_"+version] = {
                    "name": name+"_"+version,   
                    "download": self.from_url.replace("registry.txt", registry),
                    "version": version,
                    "class": _class, 
                    'binaries': [{name:name}]}

    def _local_discovery(self):

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
            if (p.parent / "registry.yaml").exists() is False: #pragma: no cover
                logger.warning("Missing registry in {}. You may use 'damona registry {} to start with".format(p.parent, p.parent))

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
        if self.from_url is None:
            from damona.recipes import __path__
            recipes = glob.glob(__path__[0] + '/*/Singularity.*')
            recipes = [os.path.basename(x) for x in recipes]
            recipes = [x.replace("Singularity.", "").lower() for x in recipes]
            recipes = [x.replace("_", ":").lower() for x in recipes]
            recipes = sorted(recipes)

            if pattern:
                recipes = [x for x in recipes if pattern in x]

            return recipes
        else:
            self._url_discovery()
            names = []
            for k,v in self.registry.items():
                names.append(k.replace("_", ":" ))
            if pattern:
                names = [x for x in names if pattern in x]
            return names
