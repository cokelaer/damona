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
##############################################################################
"""Utility helpers used across the Damona package."""
import functools
import pathlib
import shutil
import time

import colorlog
import requests
from tqdm import tqdm

logger = colorlog.getLogger(__name__)


#: Connect and read timeouts, in seconds, for image transfers.
DOWNLOAD_TIMEOUT = (10, 30)

#: Abort a transfer that has received no byte for this many seconds.
STALL_TIMEOUT = 30

#: Do not judge throughput before this many seconds have elapsed, so that a
#: slow start is not mistaken for a slow source.
SPEED_WARMUP = 5

#: Number of attempts per source before giving up on it.
MAX_ATTEMPTS = 3


class SlowSourceError(IOError):
    """Raised when a source is too slow, so that the caller can try another."""


class DownloadError(IOError):
    """Raised when every candidate source failed."""


def download_with_progress(url, filename, timeout=DOWNLOAD_TIMEOUT, stall_timeout=STALL_TIMEOUT, min_speed=None):
    """Download a file from *url* and save it to *filename* with a progress bar.

    Uses :mod:`requests` for streaming and :mod:`tqdm` to display download
    progress.  The parent directory of *filename* is created automatically if
    it does not exist.

    Two guards let a caller move on to another source rather than wait: a
    transfer that receives no byte for *stall_timeout* seconds is abandoned,
    and, when *min_speed* is set, so is one whose average throughput after a
    short warm-up stays below it. Both raise :class:`SlowSourceError`, and
    neither leaves a partial file behind.

    :param str url: The URL to download from.
    :param str filename: Destination file path (expanded and resolved).
    :param tuple timeout: ``(connect, read)`` timeouts in seconds.
    :param float stall_timeout: Abort after this long with no data received.
    :param float min_speed: Minimum average throughput in bytes per second,
        judged only after :data:`SPEED_WARMUP` seconds. ``None`` disables the
        check.
    :returns: The resolved :class:`pathlib.Path` of the downloaded file.
    :rtype: pathlib.Path
    :raises requests.HTTPError: When the server returns a non-200 status code.
    :raises SlowSourceError: When the transfer stalls or is too slow.
    """
    resp = requests.get(url, stream=True, allow_redirects=True, timeout=timeout)
    if resp.status_code != 200:
        resp.raise_for_status()
        raise RuntimeError(f"Request to {url} returned status code {resp.status_code}")

    file_size = int(resp.headers.get("Content-Length", 0))

    path = pathlib.Path(filename).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)

    desc = "(Unknown total file size)" if file_size == 0 else ""
    resp.raw.read = functools.partial(resp.raw.read, decode_content=True)  # Decompress if needed

    started = time.time()
    last_data = started
    received = 0

    try:
        with tqdm(total=file_size or None, unit="B", unit_scale=True, desc=desc) as pbar:
            with path.open("wb") as fout:
                for chunk in resp.iter_content(chunk_size=1024 * 1024):
                    now = time.time()
                    if chunk:
                        fout.write(chunk)
                        received += len(chunk)
                        pbar.update(len(chunk))
                        last_data = now
                    elif now - last_data > stall_timeout:
                        raise SlowSourceError(f"{url} sent no data for {stall_timeout}s")

                    elapsed = now - started
                    if min_speed and elapsed > SPEED_WARMUP and received / elapsed < min_speed:
                        raise SlowSourceError(
                            f"{url} is transferring at {received / elapsed / 1024:.0f} kB/s, "
                            f"below the {min_speed / 1024:.0f} kB/s floor"
                        )
    except BaseException:
        path.unlink(missing_ok=True)
        raise
    finally:
        resp.close()

    return path


def _retry_after(resp, attempt):
    """Seconds to wait before retrying, honouring ``Retry-After`` when sent."""
    header = resp.headers.get("Retry-After") if resp is not None else None
    if header:
        try:
            return min(float(header), 300)
        except (TypeError, ValueError):  # pragma: no cover - malformed header
            pass
    return min(2**attempt, 300)


def download_with_fallback(
    sources,
    filename,
    expected_md5=None,
    timeout=DOWNLOAD_TIMEOUT,
    stall_timeout=STALL_TIMEOUT,
    min_speed=None,
    max_attempts=MAX_ATTEMPTS,
):
    """Download from the first source that serves the expected bytes.

    Sources are tried in order. A source that answers 429 or 503 is retried,
    honouring ``Retry-After`` when present, before moving on. A source that is
    stalled or slower than *min_speed* is abandoned immediately, since another
    source is likely to be faster than waiting.

    When *expected_md5* is given the transferred file is verified before this
    function returns, and a mismatch is treated as a failure of that source:
    the file is discarded and the next source tried. A mirror can therefore
    never substitute different content for an artifact, whoever operates it.

    If every source trips the speed floor, the fastest one seen is retried
    once with the floor removed, so a slow network cannot make an install
    impossible.

    :param list sources: ``(name, url)`` pairs, in the order to try them.
    :param str filename: Destination file path.
    :param str expected_md5: md5 recorded in the registry for this release.
    :param tuple timeout: ``(connect, read)`` timeouts in seconds.
    :param float stall_timeout: Abort after this long with no data received.
    :param float min_speed: Minimum average throughput in bytes per second.
    :param int max_attempts: Attempts per source for retryable HTTP answers.
    :returns: ``(name, path)`` of the source that served the file.
    :rtype: tuple
    :raises DownloadError: When no source produced a valid file.
    """
    from easydev import md5 as compute_md5

    if not sources:  # pragma: no cover - defensive
        raise DownloadError("No download source available")

    failures = []
    too_slow = []

    for name, url in sources:
        for attempt in range(max_attempts):
            try:
                path = download_with_progress(
                    url, filename, timeout=timeout, stall_timeout=stall_timeout, min_speed=min_speed
                )
            except SlowSourceError as err:
                logger.warning(f"Source '{name}' abandoned: {err}")
                too_slow.append((name, url))
                failures.append(f"{name}: {err}")
                break
            except requests.HTTPError as err:
                resp = getattr(err, "response", None)
                status = getattr(resp, "status_code", None)
                if status in (429, 500, 502, 503, 504) and attempt < max_attempts - 1:
                    delay = _retry_after(resp, attempt)
                    logger.warning(f"Source '{name}' answered {status}; retrying in {delay:.0f}s")
                    time.sleep(delay)
                    continue
                logger.warning(f"Source '{name}' failed: {err}")
                failures.append(f"{name}: {err}")
                break
            except (requests.RequestException, OSError) as err:
                logger.warning(f"Source '{name}' failed: {err}")
                failures.append(f"{name}: {err}")
                break

            if expected_md5 and compute_md5(path) != expected_md5:
                logger.warning(f"Source '{name}' served content that does not match the registry md5; discarding")
                pathlib.Path(path).unlink(missing_ok=True)
                failures.append(f"{name}: md5 mismatch")
                break

            if name != sources[0][0]:
                logger.info(f"Image obtained from mirror '{name}'")
            return name, path

    if too_slow:
        name, url = too_slow[0]
        logger.warning(f"All sources were slow; retrying '{name}' without the speed floor")
        path = download_with_progress(url, filename, timeout=timeout, stall_timeout=stall_timeout, min_speed=None)
        if expected_md5 and compute_md5(path) != expected_md5:
            pathlib.Path(path).unlink(missing_ok=True)
            raise DownloadError(f"Content from '{name}' does not match the registry md5")
        return name, path

    raise DownloadError("No source could provide the image. Attempts: " + "; ".join(failures))
