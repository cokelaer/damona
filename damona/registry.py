# -*- coding: utf-8 -*-
#
#  This file is part of Damona software
#
#  Copyright (c) 2021 - Damona Development Team
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
import sys
import os
import yaml
from yaml import Loader
import packaging.version


from damona.config import Config

import colorlog
logger = colorlog.getLogger(__name__)



class Releases(dict):

    def __init__(self, data):
        # a collection of releases
        self._name = list(data.keys())[0]
        for version, release in data[self._name]['releases'].items():
            # enforce the keys to be strings
            # this is for special case of x.y that are read as float instead of
            # strings for e.g x.y.z
            self[str(version)] = Release(version, data)


class Release():
    """

    fastqc:
        binaries: # this is the main_binaries
        x.y.z:      # a version
            download:
            md5sum:
            binaries:  # this is the extra binaries
            exclude_binaries: # exclude binaries found in the main_binaries section

    """
    def __init__(self, version, data):
        """

        :param version: a valid x.y.z version to be found in data[name]['release']
            data is a dictionary 
        params: data

        """
        self._name = list(data.keys())[0]

        kwargs = data[self._name]['releases'][version]
        self.download = kwargs['download']

        if 'md5sum' not in kwargs:
            logger.debug(f"Missing md5sum entry in {self._name}. Please consider adding one ")
        self.md5sum = kwargs.get("md5sum", None)
        self._binaries = self.split_binaries(kwargs.get('binaries', []))
        self._extra_binaries = self.split_binaries(kwargs.get('extra_binaries', []))
        self._exclude_binaries = self.split_binaries(kwargs.get('exclude_binaries', []))

    def _get_binaries(self):
        binaries = self._binaries + self._extra_binaries
        binaries = [x for x in binaries if x not in self._extra_binaries]
        binaries = list(set(binaries))
        binaries = sorted(list(set(binaries)))
        if len(binaries) == 0:
            return [self._name]
        else:
            return binaries
    binaries = property(_get_binaries)

    def split_binaries(self, binaries):
        if isinstance(binaries, list):
            return binaries
        else:
            return binaries.replace(",", " ").split()

    def __repr__(self):
        binaries = ",".join(self.binaries)
        txt = f"name: {self._name}\n"
        txt += f" md5: {self.md5sum}\n"
        txt += f" binaries to be installed : {binaries}\n"
        txt += f" download from: {self.download}"
        return txt


class RemoteRegistry():
    """


    """
    def __init__(self, url):
        self.url = url
        self._read_registry()


    def _read_registry(self):

        import  urllib.request
        response = urllib.request.urlopen(self.url)
        html = response.read()
        self.rawdata = html.decode('utf-8')
        remote_registry = yaml.load(self.rawdata, Loader=Loader)
        self.data = remote_registry


class Software():
    """A class to read a given software registry


    """
    def __init__(self, name):
        """
        param name: a valid name to be found in the registry. Can also be a
            dictionary with expected registry format. 

        """

        if isinstance(name, dict):
            keys = list(name.keys())
            self.registry_name = keys[0]
            self.releases = self._interpret_registry(name)
        else:
            self.registry_name = os.path.abspath(name)
            data = self._read_registry()
            self.releases = self._interpret_registry(data)

    def _read_registry(self):
        # just an alias
        regname = self.registry_name

        if os.path.exists(regname) is False: #pragma: no cover
            raise IOError(f"incorrect input filename {regname}")

        # read the yaml
        data = yaml.load(open(regname, "r").read(), Loader=Loader)
        if len(data.keys()) != 1:
            logger.error(f"{regname} must contain on single entry named after the images. ")
            sys.exit(1)

        return data

    def _interpret_registry(self, data):
        regname = self.registry_name
        releases = Releases(data)
        self._name = releases._name
        return releases

    def _get_name(self):
        return self._name
    name = property(_get_name)

    def _get_binaries(self):
        return dict([(rel, self.releases[rel].binaries) for rel in self.releases.keys()])
    binaries = property(_get_binaries)

    def _get_versions(self):
        return sorted(self.releases.keys())
    versions = property(_get_versions)

    def _get_md5(self):
        return dict([(rel, self.releases[rel].md5sum) for rel in self.releases.keys()])
    md5 = property(_get_md5)

    def check(self):
        pass

    def __repr__(self):
        txt = f"name: {self.name}\n"
        txt += f"binaries: {self.binaries}\n"
        return txt


class Registry():
    """

    The registry contains a dictionary with all images information.

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

    def find_candidate(self, pattern):
        candidates = [x for x in self.registry.keys() if x.startswith(pattern)]
        if len(candidates) == 0:
            logger.critical(f"No image found for {pattern}. Make sure it is correct. You can use 'damona search' command")
            return None
        if len(candidates) == 1:
            return candidates[0]
        # sequana_tools_0.9.0 should return sequana_tools for the name qnd
        # 0.9.0 for the version hence the rsplit
        names = [x.rsplit(":",1)[0] for x in candidates]
        versions = [x.rsplit(":",1)[1] for x in candidates]
        version = max([packaging.version.parse(ver) for ver in versions])
        name = names[0]
        registry_name = pattern + ':' + str(version)

        return registry_name

    def discovery(self):

        if self.from_url:
            self._url_discovery()
        else:
            self._damona_discovery()

    def _url_discovery(self):
        self.registry = {}

        ext_reg = RemoteRegistry(self.from_url)

        for name, content in ext_reg.data.items():
            recipe = Software({name: content})
            recipe.check()
            name = recipe.name ##+ k.replace("Singularity.", "").lower()
            # we may have several releases
            for version in recipe.versions:
                name_version = recipe.name + ":" + version
                release = recipe.releases[version]
                if name_version not in self.registry:
                    if release.download is None:
                        logger.warning(f"recipe {recipe.name} has no download entry. please fill asap")
                    elif release.download.startswith("damona::"):
                        from_url = self.config['urls']["damona"]
                        release.download = release.download.replace("damona::", from_url)
                        release.download = release.download.replace("registry.txt", "")
                    self.registry[name_version] = release
                else: #pragma: no cover
                    for kk,vv in self.registry.items():
                        print("{}: {}".format(kk, vv))
                        for kkk,vvv in self.registry[kk].items(): 
                            print(" - {}:  {}".format(kkk, vvv))
                    raise ValueError("found a duplicated name {}".format(name_version))

    def _damona_discovery(self):

        from damona.recipes import __path__
        _registry_files = glob.glob(__path__[0] + '/*/registry.yaml')

        self.registry = {}

        for registry in _registry_files:
            recipe = Software(registry)
            recipe.check()

            for version in recipe.versions:
                name_version = recipe.name + ":" + version
                release = recipe.releases[version]
                if name_version not in self.registry:
                    if release.download is None:
                        logger.warning(f"recipe {recipe.name} has no download entry. please fill asap")
                    elif release.download.startswith("damona::"):
                        from_url = self.config['urls']["damona"]
                        release.download = release.download.replace("damona::", from_url)
                        release.download = release.download.replace("registry.txt", "")
                    self.registry[name_version] = release
                else: #pragma: no cover
                    for kk,vv in self.registry.items():
                        print("{}: {}".format(kk, vv))
                        for kkk,vvv in self.registry[kk].items(): 
                            print(" - {}:  {}".format(kkk, vvv))
                    raise ValueError("found a duplicated name {}".format(name_version))


    def get_list(self, pattern=None):
        # a name may have an underscore in it ... e.g. sequana_tools
        # in which case the singularty name is sequana_tools_0.9.0

        recipes = {}
        for name, info in self.registry.items():
            if pattern:
                if pattern in name: 
                    recipes[name] = info.download
            else:
                recipes[name] = info.download
        return recipes
