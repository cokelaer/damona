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


__all__ = ["stats", "check_mirrors"]


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


def check_mirrors(mirror=None, timeout=10):
    """Check that the declared mirrors serve what the registry says they do.

    Maintainer helper. A mirror can be declared in two places: as a base URL in
    ``damona/software/mirrors.yaml``, which applies to every release, or under
    a ``mirrors:`` key inside a release entry, which applies to that release
    only. Both are checked here.

    For each release and mirror it issues a HEAD request and compares the
    advertised ``Content-Length`` with the ``filesize`` recorded in the
    registry, which catches a mirror that is missing, stale or serving an error
    page, without transferring any image.

    A release is only checked against a mirror it actually resolves to: a
    per-release mirror is not looked for on releases that do not declare it.
    A base-URL mirror does apply to every release, so a release that has not
    been uploaded there yet is reported as ``missing``, which is the point.

    :param str mirror: restrict the check to one named mirror.
    :param float timeout: per-request timeout in seconds.
    :returns: List of ``(software, mirror, url, status)`` tuples, where status
        is ``"ok"``, ``"missing"``, ``"size-mismatch"`` or an error string.
    :rtype: list
    """
    import requests

    from damona.registry import CANONICAL_SOURCE, get_mirrors

    registry = Registry(biocontainers=False)
    bases = get_mirrors()

    # names declared globally, plus those declared by individual releases
    declared = set(bases)
    for release in registry.registry.values():
        declared |= set(getattr(release, "mirrors", {}) or {})
    declared.discard(CANONICAL_SOURCE)

    if mirror:
        if mirror not in declared:
            logger.error(f"Unknown mirror '{mirror}'. Declared mirrors: {', '.join(sorted(declared)) or 'none'}")
            return []
        declared = {mirror}

    if not declared:
        logger.warning("No mirror declared, either in damona/software/mirrors.yaml or in a release entry")
        return []

    results = []

    for name, release in tqdm.tqdm(sorted(registry.registry.items())):
        release_mirrors = getattr(release, "mirrors", {}) or {}
        for mirror_name in sorted(declared):
            # a per-release mirror only concerns the releases declaring it
            if mirror_name not in bases and mirror_name not in release_mirrors:
                continue

            url = release.mirror_url(mirror_name, mirrors=bases)
            if url is None:  # pragma: no cover - defensive
                continue

            try:
                resp = requests.head(url, allow_redirects=True, timeout=timeout)
            except requests.RequestException as err:  # pragma: no cover - network dependent
                results.append((name, mirror_name, url, f"error: {err}"))
                continue

            if resp.status_code != 200:
                results.append((name, mirror_name, url, "missing"))
                continue

            size = resp.headers.get("Content-Length")
            if release.filesize and size and int(size) != int(release.filesize):
                results.append((name, mirror_name, url, "size-mismatch"))
                continue

            results.append((name, mirror_name, url, "ok"))

    broken = [x for x in results if x[3] != "ok"]
    logger.info(f"{len(results) - len(broken)}/{len(results)} release/mirror pairs resolve")
    for item in broken:
        logger.warning(f"{item[0]} on '{item[1]}': {item[3]} ({item[2]})")

    return results


def get_software_names():
    """Return the set of unique software names available in the Damona registry.

    :returns: Set of software name strings (without version suffixes).
    :rtype: set
    """
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
                except Exception:
                    print(f"Passed {name}:{version} no docker.")
