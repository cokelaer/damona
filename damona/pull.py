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
#  website: https://github.com/cokelaer/damona
#  documentation: http://damona.readthedocs.io
#
##############################################################################
import os
from spython.main import Client
from damona import bin_directory, images_directory
from damona import Registry
from damona import logger

logger.level = 10
class Pull():
    """Manage the download of images


    """
    def __init__(self, dryrun=False):
        self.registry = Registry().registry
        self.dryrun = dryrun

    def pull(self, name, output_name=None, pull_folder=images_directory, force=False):

        # the name must be valid. we use _ to separate name and version for the
        # singularity filemane but the image have a tag (version) and name
        # separated by a :

        # Our registry uses underscore. The output filename should use _ as well
        # However, for users and image stored on sylabs or singularity hub, we
        # use the character :
        #  
        registry_name = name.replace(":", "_")
        if  registry_name not in self.registry.keys():
            logger.critical("invalid image name provided: {}. Choose amongst {}".format(name,
self.registry.keys()))
            sys.exit(1)


        download_name = self.registry[registry_name]['download']
        if output_name is None:
            output_name = registry_name + ".img"

        if self.dryrun: 
            pass
        else: # pragma: no cover
            Client.pull(download_name, name=output_name, 
                pull_folder=pull_folder,
                force=force) 
            logger.info("File {} upload to {}".format(name, images_directory))

        # Now, create an alias
        path = images_directory

        _class = self.registry[registry_name]['class']
        if _class == "exe":
            # one binary name. we use the first one
            cmd = """singularity run {}/{} ${{1+"$@"}} """
            cmd = cmd.format(images_directory, output_name)
            bin_name = bin_directory /  registry_name.split("_")[0]
            if self.dryrun: #pragma: no cover
                pass
            else: #pragma: no cover
                with open(bin_name, "w") as fout:
                    fout.write(cmd)
                os.chmod(bin_name, 0o755)
                logger.info("Binary {} in {}".format(bin_name, bin_directory))
        elif _class == "env": #pragma: no cover
            pass
        elif _class == "set": # pragma: no cover
            raise ImplementedError
        else: # pragma: no cover
            raise ValueError


