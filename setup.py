# -*- coding: utf-8 -*-
# License: 3-clause BSD
__revision__ = "$Id: $" # for the SVN Id
import sys
import os
from setuptools import setup, find_packages
import glob

_MAJOR               = 0
_MINOR               = 6
_MICRO               = 0
version              = '%d.%d.%d' % (_MAJOR, _MINOR, _MICRO)
release              = '%d.%d' % (_MAJOR, _MINOR)


metainfo = {
    'authors': {"main": ("Thomas Cokelaer", "thomas.cokelaer@pasteur.fr")},
    'maintainer': {"main": ("Thomas Cokelaer", "thomas.cokelaer@pasteur.fr")},
    'version': version,
    'license' : 'new BSD',
    'download_url': "https://github.com/sequana/sequana/archive/{0}.tar.gz".format(version),
    'url' : "http://github.com/sequana/sequana",
    'description': "A set of NGS singularity recipes, built for you and easily downlable" ,
    'platforms' : ['Linux', 'Unix'],
    'keywords' : ['NGS', 'singularity'],
    'classifiers' : [
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: BSD License',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Scientific/Engineering :: Bio-Informatics',
          'Topic :: Scientific/Engineering :: Information Analysis',
          'Topic :: Scientific/Engineering :: Mathematics',
          'Topic :: Scientific/Engineering :: Physics']
    }


packages = find_packages()
packages = [this for this in packages if this.startswith('test.') is False]
packages = [this for this in packages if this not in ['test']]

requirements = open("requirements.txt").read().split()


from setuptools import setup
from setuptools.command.develop import develop
from setuptools.command.install import install


def copyfile():
    try:
        # This is to make sure users get the newest version installed
        # If it fails, this will be copied again when calling damona for the
        # first time.
        from easydev import CustomConfig
        configuration = CustomConfig("damona", verbose=True)
        damona_config_path = configuration.user_config_dir
        with open("damona/shell/damona.sh", "r") as fin:
            with open(damona_config_path + os.sep + "damona.sh", "w") as fout:
                fout.write(fin.read())
    except:
        # could not copy the file, we will do it when starting damona for the
        # first time. 
        pass


class PostDevelopCommand(develop):
    """Post-installation for development mode."""
    def run(self):
        develop.run(self)
        copyfile()

class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        install.run(self)
        copyfile()


setup(
    name             = "damona",
    version          = version,
    maintainer       = metainfo['authors']['main'][0],
    maintainer_email = metainfo['authors']['main'][1],
    author           = metainfo['authors']['main'][0],
    author_email     = metainfo['authors']['main'][1],
    long_description = open("README.rst").read(),
    keywords         = metainfo['keywords'],
    description      = metainfo['description'],
    license          = metainfo['license'],
    platforms        = metainfo['platforms'],
    url              = metainfo['url'],
    download_url     = metainfo['download_url'],
    classifiers      = metainfo['classifiers'],

    # package installation
    packages = packages,
    install_requires = requirements,
    # specific packages for testing
    tests_require = open('requirements_dev.txt').read().split(),

    # This is recursive include of data files
    exclude_package_data = {"": ["__pycache__"]},
    package_data = {
        'damona': ['*.cfg'],
        'damona.shell': ['*.sh'],
        'damona.recipes' : ['*/Singularity.*', '*/registry.yaml'],
        '': ["damona/shell/damona.sh"]
        },

    cmdclass={"develop": PostDevelopCommand, "install": PostInstallCommand},

    zip_safe=False,
    entry_points = {
        'console_scripts':[
           'damona=damona.script:main', 
        ]
    },


)
