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
        self.releases = []

    def add_release(self, release):
        self.releases.append(release)



class Release(dict):
    def __init__(self, download, version):
        self.version = version
        self.download = download
        self.binaries = binaries


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

        if isinstance(name, dict):
            keys = list(name.keys())
            self.registry_name = keys[0]
            self.data = self._interpret_registry(name)
        else:
            self.registry_name = os.path.abspath(name)
            data = self._read_registry()
            self.data = self._interpret_registry(data)

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

        name = list(data.keys())[0]
        data = data[name]
        self._name = name
        # some checks
        if "releases" not in data.keys(): #pragma: no cover
            logger.error(f"missing 'releases' entries in {regname}")
            sys.exit(1)

        # releases may be named as x.y or x.y.z. In the former case, the x.y is
        # read as a float, and the latter as a string. We concert everything in
        # strings.
        for x in data['releases'].keys():
            if str(x) in data['releases'].keys():
                pass
            else:
                data['releases'][str(x)] = data['releases'][x].copy()
                del data['releases'][x]

        def split_binaries(binaries):
            if isinstance(binaries, list):
                return binaries
            else:
                return binaries.replace(",", " ").split()

        for release in data['releases'].keys():
            binaries = []
            if "binaries" in data.keys():
                binaries += split_binaries(data['binaries'])
            if 'binaries' in data['releases'][release].keys():
                binaries += split_binaries(data['releases'][release]['binaries'])
            if len(binaries) == 0:
                binaries = [self._name]
            binaries = sorted(list(set(binaries)))
            data['releases'][release]['binaries'] = binaries
            if 'md5sum' not in data['releases'][release]:
                logger.debug(f"Please add a md5sum in the release {release} of {regname}")

        return data

    def _get_name(self):
        return self._name
    name = property(_get_name)

    def _get_binaries(self):
        dd = self.data['releases']
        return dict([(rel, dd[rel]['binaries']) for rel in dd.keys()])
    binaries = property(_get_binaries)

    def _get_versions(self):
        return sorted(self.data['releases'].keys())
    versions = property(_get_versions)
    releases = property(_get_versions)

    def _get_md5(self):
        md5 = {}
        for x in self.releases:
            data = self.data['releases'][x]
            if 'md5sum' in data:
                md5[x] = data['md5sum']
            else:
                md5[x] = None
        return md5
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
            logger.critical(f"No image found for {pattern}. Make sure it is correct using 'damona list' com    mand")
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
            for version, release in recipe.data['releases'].items():
                name_version = name + ":" + str(version )
                if name_version not in self.registry:
                    if release['download'] is None:
                        logger.warning(f"recipe {name} has no download entry. please fill asap")

                    elif release['download'].startswith("damona::"):
                        from_url = self.config['urls']["damona"]
                        release['download'] = release['download'].replace("damona::", from_url)
                        release['download'] = release['download'].replace("registry.txt", "")
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

            name = recipe.name ##+ k.replace("Singularity.", "").lower()
            # we may have several releases
            for version, release in recipe.data['releases'].items():
                name_version = name + ":" + str(version )
                if name_version not in self.registry:
                    if release['download'] is None:
                        logger.warning(f"recipe {name} has no download entry. please fill asap")

                    elif release['download'].startswith("damona::"):
                        from_url = self.config['urls']["damona"]
                        release['download'] = release['download'].replace("damona::", from_url)
                        release['download'] = release['download'].replace("registry.txt", "")
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
        if self.from_url is None:
            from damona.recipes import __path__
            recipes = glob.glob(__path__[0] + '/*/Singularity.*')
            recipes = [os.path.basename(x) for x in recipes]
            recipes = [x.replace("Singularity.", "").lower() for x in recipes]

            # FIXME why lover here 
            new_recipes = []
            for recipe in recipes:
                if "_" not in recipe:
                    raise IOError(f'recipe must have an underscore  separating name and version: error in  "{recipe}"')
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
