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
import builtins
import os
import re
import sys

import colorlog
import tqdm

from damona import Registry, version

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
    Nb = len(set([y for x in r.get_binaries().values() for y in x]))
    Ns = len(set([x.split(":")[0] for x in r.get_list()]))
    if biocontainers:
        print("From biocontainers, in theory*, we also have:")
    print(f"- number of containers:  {Ns}")
    print(f"- version: {Nv}")
    print(f"- unique binaries: {Nb}")
    data["version"] = Nv
    data["software"] = Ns
    data["unique_binaries"] = Nb
    if biocontainers:
        print(
            """*: not all software provided in the biocontainers registry are actually on Docker.
There is nothing we can do about that in Damona. Actual number is more around 1000 public software"""
        )

    return data


def get_software_names():
    r = Registry(biocontainers=False)
    return set([x.split(":")[0] for x in r.get_list()])


def build_biocontainers_registry(output="biocontainers.yml", force=False, limit=20000):  # pragma: no cover
    """Create the list of software and their versions available in Biocontainer"""
    logger.info("Retrieve all information from Biocontainers")
    try:
        from bioservices import Biocontainers
    except (ModuleNotFoundError, ImportError) as err:
        logger.error(
            "This function is for admin only. You may use but you must install bioservices first (pip install bioservices). "
        )
        return

    logger.info("Scanning biocontainers web service")
    b = Biocontainers()

    info = b.get_tools(limit=limit)
    if len(info) > limit:
        logger.warning(f"Looks like you reached the limit of {limit} tool. Use limit argument to get more")
    tools = {}

    # Create the registry
    if os.path.exists(output) and not force:
        logger.error(f"Output file {output} exists already. Please rename or remove the target file")
        sys.exit(1)

    with open(output, "w") as fout:
        for _, tool in tqdm.tqdm(info.iterrows()):
            name = tool["name"]
            fout.write(f"{name}:\n  releases:\n")

            versions = b.get_versions_one_tool(name)
            for _, version in versions.iterrows():
                docker_images = [image for image in version.images if image["image_type"] == "Docker"]
                # Function to extract the trailing version
                import re

                def extract_version(image_name):
                    match = re.search(r"--py\d+_(\d+)$", image_name)
                    return int(match.group(1)) if match else -1  # Default to -1 if not found

                # Select the Docker image with the highest trailing version
                try:
                    most_recent_docker = builtins.max(docker_images, key=lambda img: extract_version(img["image_name"]))

                    # you may have several versions
                    image_name = most_recent_docker["image_name"]
                    fout.write(f"    {version.meta_version}:\n")
                    fout.write(f"      download: docker://{image_name}\n")
                except:
                    print(f"Passed {name}:{version} no docker.")
