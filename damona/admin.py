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
from damona import Registry
from damona.registry import Software
from damona.registry import ImageName


__all__ = ['stats']

def stats():

    r = Registry()

    names = {ImageName(x.replace(":", "_")+".img").name for x in r.get_list()}

    N = len(names)
    print(f"There are currently {N} recipes (containers) in Damona")

    N = len(r.get_list())
    print(f"These recipes include {N} versions.")

    binaries = set()
    for x in r.get_list():
        s = Software(x.split(":")[0])
        binaries = binaries.union(set(s.binaries[s.releases.last_release]))
    N = len(binaries)
    print(f"These recipes include {N} different software or environments to be installed or re-used")
