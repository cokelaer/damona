# -*- coding: utf-8 -*-
#
#  This file is part of Damona software
#
#  Copyright (c) 2020 - Damona Development Team
#
#  File author(s):
#      Thomas Cokelaer <thomas.cokelaer@pasteur.fr>
#          <d.desvillechabrol@gmail.com>
#
#  Distributed under the terms of the 3-clause BSD license.
#  The full license is in the LICENSE file, distributed with this software.
#
#  website: https://github.com/cokelaer/damona
#  documentation: http://damona.readthedocs.io
#
##############################################################################
import os
from damona import damona_config_path

# list of URLs zhere to find registry and their aliases
urls = {
    'damona':"https://biomics.pasteur.fr/drylab/damona/registry.txt"
}



class Config():

    def __init__(self):
        self.config_file = damona_config_path + os.sep + "damona.cfg"
        if os.path.exists(self.config_file) is False:
            with open(self.config_file, "w") as fout:
                fout.write("[urls]\n")
                for k,v in urls.items():
                    fout.write("{}={}".format(k,v))
        # finally we read it
        self.read()

    def read(self):
        from configparser import ConfigParser
        config = ConfigParser()
        config.read_file(open(self.config_file))
        self.config = config


 
