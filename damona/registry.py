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
from damona.config import Config


class Registry():
    """

    The registry contains a dictionary with names of images and metadata
    information about them::

        r = Registry()
        r.registry
        r.registry['prokka_1.14.5']['download']

    """

    def __init__(self, from_url=None):

        self.config = Config().config
        if from_url:
            if from_url in self.config['urls']:
                from_url = self.config['urls'][from_url]
            else:
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
                try:
                    package, tools = registry.split(maxsplit=1)
                except:
                    tools = []
                    package = registry

                if package.count('_') == 0:
                    logger.warning("invalid name {}".format(package))
                elif package.count("_") == 1:
                    name, version = package.split("_")
                else:
                    name, version = package.rsplit("_", 1)
                version = version.rsplit(".", 1)[0]
                # todo for now only exe fills the binaries assuming name of
                # package is the name of the binary
                if _class in ["exe", 'env']:
                    binaries= [{name:name}]
                else:
                    binaries = tools
                self.registry[name+"_"+version] = {
                    "name": name+"_"+version,   
                    "download": self.from_url.replace("registry.txt", package),
                    "version": version,
                    "class": _class, 
                    'binaries': binaries}

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
        # a name may have an underscore in it ... e.g. sequana_tools
        # in which case the singularty name if sequana_tools_0.9.0
        if self.from_url is None:
            from damona.recipes import __path__
            recipes = glob.glob(__path__[0] + '/*/Singularity.*')
            recipes = [os.path.basename(x) for x in recipes]
            recipes = [x.replace("Singularity.", "").lower() for x in recipes]

            # FIXME why lover here 
            new_recipes = []
            for recipe in recipes:
                if "_" not in recipe:
                    raise IOError('recipe must have an underscore t separate name and version')
                else:
                    #replace only last occurence
                    recipe = recipe[::-1].replace("_", ":", 1)[::-1]
                new_recipes.append(recipe.lower())
            recipes = sorted(new_recipes)

            if pattern:
                recipes = [x for x in recipes if pattern in x]

            return recipes
        else:
            self._url_discovery()
            names = []
            for k,v in self.registry.items():
                names.append(k[::-1].replace("_", ":",1)[::-1])
            if pattern:
                names = [x for x in names if pattern in x]
            return names
