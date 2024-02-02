#
#  This file is part of Damona software
#
#  Copyright (c) 2020 - Damona Development Team
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
import functools
import pathlib
import shutil

import requests
from tqdm import tqdm


def download_with_progress(url, filename):
    """Download image/container from a URL.

    :param filename: where to save the container


    """
    resp = requests.get(url, stream=True, allow_redirects=True)
    if resp.status_code != 200:
        resp.raise_for_status()
        raise RuntimeError(f"Request to {url} returned status code {r.status_code}")

    file_size = int(resp.headers.get("Content-Length", 0))

    path = pathlib.Path(filename).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)

    desc = "(Unknown total file size)" if file_size == 0 else ""
    resp.raw.read = functools.partial(resp.raw.read, decode_content=True)  # Decompress if needed
    with tqdm.wrapattr(resp.raw, "read", total=file_size, desc=desc) as fout:
        with path.open("wb") as f:
            shutil.copyfileobj(fout, f)
    return path
