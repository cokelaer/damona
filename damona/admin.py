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
from damona import Registry
from damona.registry import Software
from damona.registry import ImageName
from damona import version

__all__ = ["stats"]


def stats():
    """Prints statistics about Damona

    ::

        from damona.admin import stats
        stats()

    """

    r = Registry()

    names = {ImageName(x.replace(":", "_") + ".img").name for x in r.get_list()}
    N = len(r.get_list())

    print(f"- version: {version}")
    print(f"- number of recipes:  {len(names)}")
    print(f"- number of versions: {N}")

    binaries = set()
    for x in r.get_list():
        s = Software(x.split(":")[0])
        binaries = binaries.union(set(s.binaries[s.releases.last_release]))
    N = len(binaries)
    print(f"- unique binaries: {N}")
