#
#  This file is part of Damona software
#
#  Copyright (c) 2020-2021 - Damona Development Team
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
"""Provide some stats for admin"""
import os
import sys

from damona import Registry
from damona.registry import Software
from damona.registry import ImageName
from damona import version

import colorlog

logger = colorlog.getLogger(__name__)


__all__ = ["stats"]


def stats(biocontainers=False):
    """Prints statistics about Damona

    It includes the number of software and their releases.
    It also includes the nmbr of binaries.

    ::

        from damona.admin import stats
        stats()

    """

    data = {}
    print(f"Damona version : {version}")
    r = Registry(biocontainers=biocontainers)

    Nv = len(r.get_list())
    Nb = sum([len(x) for x in r.get_binaries().values()])
    Ns = len(set([x.split(":")[0] for x in r.get_list()]))
    if biocontainers:
        print("From biocontainers, in theory*, we also have:")
    print(f"- number of software:  {Ns}")
    print(f"- version: {Nv}")
    print(f"- unique binaries: {Nb}")
    data["version"] = Nv
    data["software"] = Ns
    data["unique_binaries"] = Nb
    if biocontainers:
        print("""*: not all software provided in the biocontainers registry are actually on Docker.
There is nothing we can do about that in Damona. Actual number is more around 1000 public software""")

    return data


def build_biocontainers_registry(output="biocontainers.yml", force=False, limit=20000): #pragma: no cover
    """Create the list of software and their versions available in Biocontainer"""
    logger.info("Retrieve all information from Biocontainers")
    try:
        from bioservices import Biocontainers
    except (ModuleNotFoundError, ImportError) as err:
        logger.error("This function is for admin only. You may use but you mut install bioservices first (pip install bioservices). ")
        return 

    b = Biocontainers()
    info = b.get_tools(limit=limit)
    if len(info) > limit:
        logger.warning(f"Looks like you reached the limit of {limit} tool. Use limit argument to get more")
    tools = {}
    for name, versions in zip(info['name'], info['versions']):
        tools[name] = [x['meta_version'] for x in versions]

    # Create the registry
    if os.path.exists(output) and not force:
        logger.error(f"Output file {output} exists already. Please rename or remove the target file")
        sys.exit(1)

    with open(output, "w") as fout:
        for name, versions in tools.items():
            fout.write(f"{name}:\n  releases:\n")
            for version in versions:
                fout.write(f"    {version}:\n")
                fout.write(f"      download: docker://biocontainers/{name}:{version}\n")

