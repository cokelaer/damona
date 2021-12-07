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
"""Registry and Software manager"""
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


__all__ = ["Releases", "Software", "Registry", "Release", "ImageName"]


class ImageName:
    """

    An image name must have the following convention::

        name_x.y.z.img

    or::

        name_other_x.y.z.img

    """

    def __init__(self, name):

        self.filename = name
        self.basename = os.path.basename(name)

        if not self.basename.endswith(".img"):
            logger.error("Input file name must follow the convention NAME_x.y.z.img You provided {self.basename}")
            raise NameError

        if "_" not in self.basename:
            logger.error("Input file name must follow the convention NAME_x.y.z.img You provided {self.basename}")
            raise NameError

        name, version = self.basename.rsplit(".", 1)[0].rsplit("_", 1)
        self.name = name
        self.version = version

        # check version
        if len(version.split(".")) not in [2, 3]:
            raise NameError


class Releases(dict):
    """A collection of :class:`Release`."""

    def __init__(self, data):
        # a collection of releases
        self._name = list(data.keys())[0]

        if "releases" not in data[self._name]:
            pass
        else:
            for version, release in data[self._name]["releases"].items():
                # enforce the keys to be strings
                # this is for special case of x.y that are read as float instead of
                # strings for e.g x.y.z
                self[str(version)] = Release(version, data)

    def _get_last_release(self):
        from packaging import version

        return max(list(self.keys()), key=lambda x: version.parse(x))

    last_release = property(_get_last_release)


class Release:
    """A Release class

    This class populates information found in the release section of a
    registry.

    A regitry looks like::

        fastqc:
            binaries: # this is the main_binaries
            x.y.z:      # a version
                download:
                md5sum:
                binaries:  # this is the extra binaries
                exclude_binaries: # exclude binaries found in the main_binaries section

    Here we have one release named x.y.z that contains information about the
    md5sum of the container, its location, and the binaries that should be
    installed.

    If binaries of the software is empty, we use the one in the specific release.
    If no binaries are set, we use the name of the software. Duplicated are
    ignored of course.

    So future release may change the list of binaries. exclude_binaries is set
    can be used to remove such binaries

    binaries can be separated by commas or spaces.

    """

    def __init__(self, version, data):
        """

        :param version: a valid x.y.z version to be found in data[name]['release']
            data is a dictionary
        :param data:

        """
        self._name = list(data.keys())[0]

        try:
            self._binaries = self.split_binaries(data[self._name].get("binaries", []))
            kwargs = data[self._name]["releases"][version]
            self.download = kwargs["download"]
        except Exception as err:  # pragma: no cover
            logger.error(f"Incorrect formatted registry for {self._name}" + str(err))
            sys.exit(1)

        if "md5sum" not in kwargs:
            logger.debug(f"Missing md5sum entry in {self._name}. Please consider adding one ")
        self.md5sum = kwargs.get("md5sum", None)
        self._release_binaries = self.split_binaries(kwargs.get("binaries", []))
        self._extra_binaries = self.split_binaries(kwargs.get("extra_binaries", []))
        self._exclude_binaries = self.split_binaries(kwargs.get("exclude_binaries", []))
        self._data = data

    def _get_binaries(self):
        binaries = self._binaries + self._release_binaries + self._extra_binaries
        binaries = [x for x in binaries if x not in self._exclude_binaries]
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


class RemoteRegistry:
    """ """

    def __init__(self, url):
        self.url = url
        self._read_registry()

    def _read_registry(self):

        import urllib.request

        response = urllib.request.urlopen(self.url)
        html = response.read()
        self.rawdata = html.decode("utf-8")
        remote_registry = yaml.load(self.rawdata, Loader=Loader)
        self.data = remote_registry


class Software:
    """A class to read a given software registry

    A Software is made of :class:`Releases`. It contains also a name, a list of
    binaries either globally or per release

    ::

        registry.Software("fastqc")

    prints:

        name: fastqc
        binaries: {'0.11.9': ['fastqc'], '0.11.8': ['fastqc']}


    """

    def __init__(self, name):
        """

        :param name: a valid name to be found in the registry. Can also be a
            dictionary with expected registry format.

        """

        if isinstance(name, dict):
            # Use when calling with --url
            keys = list(name.keys())
            self.registry_name = keys[0]
            #: a :class:`Releases` attribute
            self.releases = self._interpret_registry(name)
        # we are interested in existing local YAML files
        elif os.path.exists(name) and not os.path.isdir(name):
            # print("Existing path or name")
            self.registry_name = os.path.abspath(name)
            data = self._read_registry()
            #: a :class:`Releases` attribute
            self.releases = self._interpret_registry(data)
        # directory to be found in damona directory
        else:
            from damona import __path__

            self.registry_name = pathlib.Path(__path__[0]) / "recipes" / name / "registry.yaml"
            data = self._read_registry()
            self._data = data
            if len(data):
                self.releases = self._interpret_registry(data)
                self.doi = data[self.name].get("doi", None)
                self.zenodo_id = data[self.name].get("zenodo_id", None)
            else:  # pragma: no cover
                self._name = None
                self._version = None

    def _read_registry(self):
        # just an alias
        regname = self.registry_name

        if os.path.exists(regname) is False:  # pragma: no cover
            logger.warning(f"Input software not found in {regname}")
            return {}

        # read the yaml

        data = yaml.load(open(regname, "r").read(), Loader=Loader)
        if len(data.keys()) != 1:  # pragma: no cover
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
        txt += f"releases: {self.releases}\n"
        return txt


class Registry:
    """

    The registry contains a dictionary with all images information.::

        r = Registry()
        r.registry
        r.registry['prokka_1.14.5']['download']
        r.registry['prokka_1.14.5']['binaries']

    """

    def __init__(self, from_url=None):

        self.config = Config().config
        if from_url:
            if from_url in self.config["urls"]:
                from_url = self.config["urls"][from_url]
            else:  # pragma: no cover
                assert from_url.startswith("http")
                assert from_url.endswith("registry.txt")
        self.from_url = from_url
        self.registry = {}
        self.discovery()

    def find_candidate(self, pattern):
        """Find a unique recipe within the registry.


        Note for developers: not the same as get_list"""
        candidates = [x for x in self.registry.keys() if pattern in x]
        if len(candidates) == 0:  # pragma: no cover
            logger.critical(
                f"No image found for {pattern}. Make sure it is correct. You can use 'damona search' command"
            )
            return None

        if len(candidates) == 1:
            return candidates[0]

        # sequana_tools_0.9.0 should return sequana_tools for the name and
        # 0.9.0 for the version hence the rsplit
        names = [x.rsplit(":", 1)[0] for x in candidates]
        versions = [x.rsplit(":", 1)[1] for x in candidates]
        version = max([packaging.version.parse(ver) for ver in versions])
        name = names[0]
        registry_name = pattern + ":" + str(version)

        return registry_name

    def discovery(self):
        """Look for recipes in the registry and populate the attributes"""
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
            name = recipe.name  ##+ k.replace("Singularity.", "").lower()
            # we may have several releases
            for version in recipe.versions:
                name_version = recipe.name + ":" + version
                release = recipe.releases[version]
                if name_version not in self.registry:
                    if release.download is None:  # pragma: no cover
                        logger.warning(f"recipe {recipe.name} has no download entry. please fill asap")
                    elif release.download.startswith("damona::"):  # pragma: no cover
                        from_url = self.config["urls"]["damona"]
                        release.download = release.download.replace("damona::", from_url)
                        release.download = release.download.replace("registry.txt", "")
                    self.registry[name_version] = release
                else:  # pragma: no cover
                    for kk, vv in self.registry.items():
                        print("{}: {}".format(kk, vv))
                        for kkk, vvv in self.registry[kk].items():
                            print(" - {}:  {}".format(kkk, vvv))
                    raise ValueError("found a duplicated name {}".format(name_version))

    def _damona_discovery(self):

        from damona.recipes import __path__

        _registry_files = glob.glob(__path__[0] + "/*/registry.yaml")

        self.registry = {}

        for registry in _registry_files:
            recipe = Software(registry)
            recipe.check()

            for version in recipe.versions:
                name_version = recipe.name + ":" + version
                release = recipe.releases[version]
                if name_version not in self.registry:
                    if release.download is None:  # pragma: no cover
                        logger.warning(f"recipe {recipe.name} has no download entry. please fill asap")
                    elif release.download.startswith("damona::"):
                        from_url = self.config["urls"]["damona"]
                        release.download = release.download.replace("damona::", from_url)
                        release.download = release.download.replace("registry.txt", "")
                    self.registry[name_version] = release
                else:  # pragma: no cover
                    for kk, vv in self.registry.items():
                        print("{}: {}".format(kk, vv))
                        for kkk, vvv in self.registry[kk].items():
                            print(" - {}:  {}".format(kkk, vvv))
                    raise ValueError("found a duplicated name {}".format(name_version))

    def get_list(self, pattern=None):
        """Return list of :class:`Software` found in the registry"""
        recipes = {}
        for name, info in self.registry.items():
            if pattern:
                if pattern.lower() in name.lower():
                    recipes[name] = info.download
            else:
                recipes[name] = info.download
        recipes = sorted(recipes)
        return recipes

    def get_binaries(self, pattern=None):
        """Return binaries found and from which recipe"""
        recipes = {}
        for name, info in self.registry.items():
            if pattern:
                if pattern.lower() in [x.lower() for x in info.binaries]:
                    recipes[name] = [x for x in info.binaries if pattern.lower() in x.lower()]
            else:
                recipes[name] = info.binaries
        return recipes
