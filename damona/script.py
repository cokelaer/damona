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
import subprocess
from damona  import version, bin_directory, images_directory
from spython.main import Client
import pathlib

__all__ = ["main"]

from damona import logger
logger.level = 10


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
@click.argument('filename', required=True, type=click.STRING)
@click.option('--output-name', default=None, 
    help="default to the singularity extension and tag")
def build(**kwargs):
    """Build a local image. You must have sudo permissions
    If FILENAME is not local, try to find it in Damona and build it.

        # a local recipes
        damona build ./Singularity.recipe

       # a recipe to be found in damona
        damona build salmon:1.3.0

    """
    cmd = "sudo singularity build {} {}"
    output_name = kwargs.get('output_name')
    if output_name is None:
        # get filename and save locally
        output_name = str(pathlib.Path(kwargs['filename']).name)
        output_name = output_name.replace("Singularity.", "")
        output_name = output_name.replace(":", "_") + ".img"
    else:
        assert output_name.endswith(('.sif', 'img'))

    if os.path.exists(kwargs['filename']):
        cmd = cmd.format(output_name, kwargs['filename'])
    else:
        from damona import registry
        reg = registry.Registry()
        user_name = kwargs['filename']
        candidate = [x for x in reg._singularity_files 
            if x.endswith(user_name.replace(':', '_', 1))]
        if len(candidate) == 0:
            logger.critical(f'unknown image name {user_name}. use the command' +
                ' "damona list" to get correct names')
            sys.exit(1)
        logger.info("Building using damona recipes for {}".format(candidate[0]))
        cmd = cmd.format(output_name, candidate[0].replace(':', '_'))
    subprocess.call(cmd.split())


@main.command()
@click.option('--pattern', default=None, 
    help="restrict the output list keeping those with this pattern")
def list(**kwargs):
    """List all available images from Damona"""
    from damona.registry import Registry
    modules = Registry().get_list(pattern=kwargs['pattern'])
    print(", ".join(modules))


@main.command()
@click.option('--path', required=True, 
    help="path to recipes directory where Singularity file(s) can be found")
def develop(**kwargs):
    """Developers kit (eg build registry)"""
    from damona.registry import Registry
    if kwargs['path']:
        modules = Registry().create_registry(kwargs['path'])

if __name__ == "__main__": #pragma: no cover
    main()
