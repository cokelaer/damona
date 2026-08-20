"""Mirror resolution and multi-source download.

Every test here is offline: requests.get is replaced by a fake that serves
bytes, stalls, or answers 429/503 on demand.
"""

import hashlib
import time

import pytest
import requests

from damona.registry import CANONICAL_SOURCE, Release, get_mirrors
from damona.utils import (
    DownloadError,
    SlowSourceError,
    download_with_fallback,
    download_with_progress,
)

MIRRORS = {"pasteur": "https://mirror.pasteur.fr/damona", "ifb": "https://mirror.ifb.fr/damona"}

PAYLOAD = b"a singularity image" * 100
PAYLOAD_MD5 = hashlib.md5(PAYLOAD).hexdigest()


def make_release(mirrors=None):
    release = {
        "download": "https://zenodo.org/record/5708820/files/art_2.5.8.img",
        "md5sum": PAYLOAD_MD5,
        "filesize": len(PAYLOAD),
        "doi": "10.5281/zenodo.5708820",
    }
    if mirrors:
        release["mirrors"] = mirrors
    return Release("2.5.8", {"art": {"binaries": "art_illumina", "releases": {"2.5.8": release}}})


class FakeResponse:
    """Minimal stand-in for a streamed requests response."""

    def __init__(self, chunks, status_code=200, headers=None, delay=0):
        self._chunks = chunks
        self.status_code = status_code
        self.headers = headers or {"Content-Length": str(sum(len(c) for c in chunks))}
        self._delay = delay
        self.raw = type("raw", (), {"read": lambda *a, **k: b""})()

    def iter_content(self, chunk_size=None):
        for chunk in self._chunks:
            if self._delay:
                time.sleep(self._delay)
            yield chunk

    def raise_for_status(self):
        if self.status_code != 200:
            error = requests.HTTPError(f"{self.status_code}")
            error.response = self
            raise error

    def close(self):
        pass


def serve(mapping):
    """Build a requests.get replacement dispatching on URL."""

    def _get(url, **kwargs):
        response = mapping[url]
        return response() if callable(response) else response

    return _get


# --------------------------------------------------------------- registry side


def test_mirrors_file_is_readable():
    # shipped file may declare no mirror yet, but must parse
    assert isinstance(get_mirrors(), dict)


def test_url_is_derived_from_the_mirror_base():
    release = make_release()
    assert release.filename == "art_2.5.8.img"
    assert release.mirror_url("pasteur", mirrors=MIRRORS) == "https://mirror.pasteur.fr/damona/art_2.5.8.img"
    assert release.mirror_url(CANONICAL_SOURCE, mirrors=MIRRORS) == release.download


def test_per_release_override_wins_over_the_base():
    release = make_release(mirrors={"pasteur": "https://mirror.pasteur.fr/damona/renamed.img"})
    assert release.mirror_url("pasteur", mirrors=MIRRORS) == "https://mirror.pasteur.fr/damona/renamed.img"


def test_default_order_is_canonical_then_mirrors():
    names = [name for name, _ in make_release().download_urls(mirrors=MIRRORS)]
    assert names == [CANONICAL_SOURCE, "pasteur", "ifb"]


def test_explicit_source_returns_only_that_one():
    sources = make_release().download_urls(source="ifb", mirrors=MIRRORS)
    assert sources == [("ifb", "https://mirror.ifb.fr/damona/art_2.5.8.img")]


def test_unknown_source_lists_the_valid_names():
    with pytest.raises(ValueError) as err:
        make_release().download_urls(source="nowhere", mirrors=MIRRORS)
    assert "zenodo" in str(err.value) and "pasteur" in str(err.value)


# --------------------------------------------------------------- download side


def test_fallback_uses_the_next_source_after_a_failure(mocker, tmpdir):
    release = make_release()
    sources = release.download_urls(mirrors=MIRRORS)
    mocker.patch(
        "requests.get",
        side_effect=serve(
            {
                sources[0][1]: FakeResponse([], status_code=503),
                sources[1][1]: FakeResponse([PAYLOAD]),
            }
        ),
    )
    mocker.patch("time.sleep")  # do not wait out the backoff

    name, path = download_with_fallback(
        sources[:2], str(tmpdir / "art_2.5.8.img"), expected_md5=PAYLOAD_MD5, max_attempts=1
    )
    assert name == "pasteur"
    assert path.read_bytes() == PAYLOAD


def test_a_503_is_retried_before_falling_through(mocker, tmpdir):
    answers = [FakeResponse([], status_code=503, headers={"Retry-After": "1"}), FakeResponse([PAYLOAD])]
    mocker.patch("requests.get", side_effect=lambda url, **kw: answers.pop(0))
    sleep = mocker.patch("time.sleep")

    name, path = download_with_fallback(
        [("zenodo", "https://zenodo.org/x.img")], str(tmpdir / "x.img"), expected_md5=PAYLOAD_MD5
    )
    assert name == "zenodo"
    assert sleep.call_args[0][0] == 1  # Retry-After honoured, not the default backoff


def test_a_mirror_serving_other_content_is_rejected(mocker, tmpdir):
    """Wrong bytes must fail closed and fall through, never be installed."""
    sources = [("evil", "https://evil.example/x.img"), ("zenodo", "https://zenodo.org/x.img")]
    mocker.patch(
        "requests.get",
        side_effect=serve(
            {
                sources[0][1]: FakeResponse([b"not the image at all"]),
                sources[1][1]: FakeResponse([PAYLOAD]),
            }
        ),
    )

    destination = tmpdir / "x.img"
    name, path = download_with_fallback(sources, str(destination), expected_md5=PAYLOAD_MD5)
    assert name == "zenodo"
    assert path.read_bytes() == PAYLOAD


def test_every_source_bad_raises_rather_than_installing(mocker, tmpdir):
    sources = [("a", "https://a/x.img"), ("b", "https://b/x.img")]
    mocker.patch(
        "requests.get",
        side_effect=serve({url: FakeResponse([b"wrong"]) for _, url in sources}),
    )
    destination = tmpdir / "x.img"
    with pytest.raises(DownloadError):
        download_with_fallback(sources, str(destination), expected_md5=PAYLOAD_MD5)
    assert not destination.exists()


def test_a_slow_source_is_abandoned(mocker, tmpdir):
    """A transfer below the floor raises so the caller can try elsewhere."""
    chunks = [b"x" * 1000] * 4
    mocker.patch("requests.get", return_value=FakeResponse(chunks, delay=0.05))
    mocker.patch("damona.utils.SPEED_WARMUP", 0)

    destination = tmpdir / "slow.img"
    with pytest.raises(SlowSourceError):
        download_with_progress("https://slow/x.img", str(destination), min_speed=10 * 1024 * 1024)
    assert not destination.exists()  # no partial file left behind


def test_a_slow_source_is_still_used_when_it_is_the_only_one(mocker, tmpdir):
    """A slow network must not make an install impossible."""
    mocker.patch("requests.get", side_effect=lambda url, **kw: FakeResponse([PAYLOAD], delay=0.05))
    mocker.patch("damona.utils.SPEED_WARMUP", 0)

    name, path = download_with_fallback(
        [("zenodo", "https://slow/x.img")],
        str(tmpdir / "x.img"),
        expected_md5=PAYLOAD_MD5,
        min_speed=10 * 1024 * 1024,
    )
    assert name == "zenodo"
    assert path.read_bytes() == PAYLOAD


def test_a_stalled_transfer_is_abandoned(mocker, tmpdir):
    mocker.patch("requests.get", return_value=FakeResponse([b"x" * 10, b"", b""], delay=0.05))

    destination = tmpdir / "stalled.img"
    with pytest.raises(SlowSourceError):
        download_with_progress("https://stalled/x.img", str(destination), stall_timeout=0.01)
    assert not destination.exists()


# ------------------------------------------------- the shipped helloworld entry
#
# helloworld is the reference case for the mirror syntax: a real release, on
# Zenodo, with a real second source. These tests keep the shipped registry and
# the mirror honest rather than exercising the code against a fixture.

HELLOWORLD = "helloworld:1.0.0"


def shipped_release():
    from damona.registry import Registry

    return Registry(biocontainers=False).registry[HELLOWORLD]


def online(url):
    try:
        return requests.head(url, allow_redirects=True, timeout=10).status_code == 200
    except requests.RequestException:
        return False


def mirrored_releases():
    from damona.registry import Registry

    registry = Registry(biocontainers=False)
    return {name: release for name, release in registry.registry.items() if getattr(release, "mirrors", None)}


def test_every_mirrored_release_is_well_formed():
    """Guard the mirror syntax across the whole catalogue, not one entry.

    Grows by itself: each release that gains a mirrors block is checked here
    for the fields a fall-through needs, so a typo in a new entry fails the
    suite rather than surfacing as a failed install.
    """
    releases = mirrored_releases()
    assert HELLOWORLD in releases  # the reference entry must keep its mirror

    for name, release in releases.items():
        assert release.md5sum, f"{name} declares a mirror but no md5sum to verify it against"
        assert release.filesize, f"{name} declares a mirror but no filesize"
        sources = release.download_urls()
        assert sources[0][0] == CANONICAL_SOURCE, f"{name} must try its own URL first"
        for mirror_name in release.mirrors:
            url = release.mirror_url(mirror_name)
            assert url and url.startswith("http"), f"{name} mirror '{mirror_name}' does not resolve"
            assert (mirror_name, url) in sources


def test_declared_mirrors_serve_the_recorded_size():
    """Every declared mirror must hold the image the registry describes.

    A HEAD per mirror, so the cost stays flat as mirroring is rolled out; the
    byte-level check is done once, on the small helloworld image, below.
    """
    releases = mirrored_releases()

    for name, release in releases.items():
        for mirror_name, url in release.mirrors.items():
            try:
                resp = requests.head(url, allow_redirects=True, timeout=15)
            except requests.RequestException:  # pragma: no cover - offline
                pytest.skip(f"{url} unreachable")
            assert resp.status_code == 200, f"{name} on '{mirror_name}' answered {resp.status_code}"
            size = resp.headers.get("Content-Length")
            if size:
                assert int(size) == int(release.filesize), f"{name} on '{mirror_name}' has the wrong size"


def test_helloworld_declares_a_usable_mirror():
    """The shipped entry must parse and expose both sources, canonical first."""
    release = shipped_release()
    assert "sequana" in release.mirrors
    assert [name for name, _ in release.download_urls()] == [CANONICAL_SOURCE, "sequana"]
    assert release.mirror_url("sequana") == release.mirrors["sequana"]
    assert release.md5sum and release.filesize


def test_helloworld_mirror_serves_the_same_artifact(tmpdir):
    """The mirror is only a mirror if its bytes match the registry md5.

    This is the acceptance test a new mirror has to pass: same checksum as the
    Zenodo deposit, so an install served by it is indistinguishable.
    """
    release = shipped_release()
    url = release.mirror_url("sequana")
    if not online(url):  # pragma: no cover - offline or mirror down
        pytest.skip(f"{url} unreachable")

    name, path = download_with_fallback(
        release.download_urls(source="sequana"),
        str(tmpdir / "helloworld_1.0.0.img"),
        expected_md5=release.md5sum,
    )
    assert name == "sequana"
    assert path.stat().st_size == release.filesize


def test_helloworld_falls_back_to_the_mirror(tmpdir):
    """A dead primary must fall through to the mirror, still checksum-verified."""
    release = shipped_release()
    url = release.mirror_url("sequana")
    if not online(url):  # pragma: no cover - offline or mirror down
        pytest.skip(f"{url} unreachable")

    sources = [("broken", "https://mirror.invalid.example/helloworld_1.0.0.img")] + release.download_urls(
        source="sequana"
    )
    name, path = download_with_fallback(
        sources, str(tmpdir / "helloworld_1.0.0.img"), expected_md5=release.md5sum, max_attempts=1
    )
    assert name == "sequana"
    assert path.stat().st_size == release.filesize


def test_check_mirrors_sees_per_release_declarations(mocker):
    """A mirror declared only inside a release must still be checked.

    mirrors.yaml is empty while mirroring is rolled out entry by entry, so a
    checker that only read that file would report nothing to do.
    """
    from damona import admin

    heads = []

    class _Head:
        status_code = 200

        def __init__(self, size):
            self.headers = {"Content-Length": str(size)}

    def fake_head(url, **kwargs):
        heads.append(url)
        release = [r for r in mirrored_releases().values() if url in r.mirrors.values()][0]
        return _Head(release.filesize)

    mocker.patch("requests.head", side_effect=fake_head)
    results = admin.check_mirrors()

    assert results, "per-release mirrors were ignored"
    assert all(status == "ok" for _, _, _, status in results)
    assert len(heads) == sum(len(r.mirrors) for r in mirrored_releases().values())


def test_check_mirrors_reports_a_size_mismatch(mocker):
    """A mirror holding a different file must be reported, not passed."""
    from damona import admin

    class _Head:
        status_code = 200
        headers = {"Content-Length": "1"}

    mocker.patch("requests.head", return_value=_Head())
    results = admin.check_mirrors()

    assert results and all(status == "size-mismatch" for _, _, _, status in results)


def test_check_mirrors_rejects_an_unknown_name():
    from damona import admin

    assert admin.check_mirrors(mirror="nowhere") == []
