# -*- coding: utf-8 -*-

###########################################################################
# Bioconvert is a project to facilitate the interconversion               #
# of life science data from one format to another.                        #
#                                                                         #
# Authors: see CONTRIBUTORS.rst                                           #
# Copyright © 2018  Institut Pasteur, Paris and CNRS.                     #
# See the COPYRIGHT file for details                                      #
#                                                                         #
# bioconvert is free software: you can redistribute it and/or modify      #
# it under the terms of the GNU General Public License as published by    #
# the Free Software Foundation, either version 3 of the License, or       #
# (at your option) any later version.                                     #
#                                                                         #
# bioconvert is distributed in the hope that it will be useful,           #
# but WITHOUT ANY WARRANTY; without even the implied warranty of          #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the           #
# GNU General Public License for more details.                            #
#                                                                         #
# You should have received a copy of the GNU General Public License       #
# along with this program (COPYING file).                                 #
# If not, see <http://www.gnu.org/licenses/>.                             #
###########################################################################
""".. rubric:: Standalone application dedicated to conversion"""
import os
import argparse
import glob
import json
import sys
import colorlog
import textwrap
import click
from damona  import version, bin_directory, images_directory
from spython.main import Client

_log = colorlog.getLogger(__name__)
_log.level = "INFO"

def error(msg):
    _log.error(msg)
    sys.exit(1)

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


# TODO: this should be automatic somehow
registry = ["bcl2fastq", "fastqc", "r_4.0.2", "r_3.6.3"]

@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version=version)
def main():
    """This is the main help"""
    pass


@main.command()
@click.argument('name')
@click.option('--force', is_flag=True)
@click.option('--output-directory', default=images_directory)
#@click.option('--name', default='bcl2fastq', help='word to use for the greeting')
def pull(**kwargs):
    "Download an image given its name and version (optional)"
    name = kwargs['name']


    # TODO: must be valid 
    #_log.info("Downloading image names {}".format(name))
    try:
        Client.pull(f"shub://cokelaer/damona:{name}", name=name.split()[0] + ".img",
            pull_folder=kwargs["output_directory"], force=kwargs['force'])

    except:
        # If it fails, this may be a normal behaviour
        pass

@main.command()
#@click.argument('name', help_option_names="dddd")
#@click.option('--name', default='bcl2fastq', help='word to use for the greeting')
def list(**kwargs):
    "List all available images"
    print(", ".join(registry))




if __name__ == "__main__":
    main()
