# -*- coding: utf-8 -*-

###########################################################################
# Damona is a project to provide reproducible containers                  #
#                                                                         #
# Authors: see CONTRIBUTORS.rst                                           #
# Copyright © 2020  Institut Pasteur, Paris and CNRS.                     #
# See the COPYRIGHT file for details                                      #
#                                                                         #
# Damona is free software: you can redistribute it and/or modify          #
# it under the terms of the GNU General Public License as published by    #
# the Free Software Foundation, either version 3 of the License, or       #
# (at your option) any later version.                                     #
#                                                                         #
# Damona  is distributed in the hope that it will be useful,              #
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

__all__ = ["main"]

_log = colorlog.getLogger(__name__)
_log.level = "INFO"


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])



@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version=version)
def main():
    """This is the main help"""
    pass


@main.command()
@click.argument('name', type=click.STRING)
@click.option('--force', is_flag=True)
@click.option('--dryrun', is_flag=True, 
    help="If set, do not pull the image and do not create the binary alias")
@click.option('--output-directory', default=images_directory, 
    help="""Where to save the image (default: {})""".format(images_directory))
def pull(**kwargs):
    "Download an image given its name and version (optional)"
    name = kwargs['name']
    from damona.pull import Pull
    p = Pull(dryrun=kwargs['dryrun'])
    p.pull(name, pull_folder=kwargs["output_directory"],
        force=kwargs['force'])


@main.command()
@click.option('--pattern', default=None, 
    help="restrict the output list keeping those with this pattern")
def list(**kwargs):
    """List all available images"""
    from damona.registry import Registry
    modules = Registry().get_list(pattern=kwargs['pattern'])
    print(", ".join(modules))


@main.command()
@click.option('--path', required=True, 
    help="path to recipes directory where Singularity file(s) can be found")
def develop(**kwargs):
    """tools for developers only"""
    from damona.registry import Registry
    if kwargs['path']:
        modules = Registry().create_registry(kwargs['path'])






if __name__ == "__main__": #pragma: no cover
    main()
