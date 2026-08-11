import sys
from unittest.mock import MagicMock

import pytest

import damona
from damona import zenodo
from damona.registry import ImageName

from . import test_dir

deposit = {
    "conceptdoi": "10.5072/zenodo.960007",
    "conceptrecid": "960007",
    "created": "2021-11-13T20:15:42.926938+00:00",
    "doi": "10.5072/zenodo.960008",
    "doi_url": "https://doi.org/10.5072/zenodo.960008",
    "files": [
        {
            "checksum": "4949d8da803d970e74de7ce898ed3c6b",
            "filename": "art_2.5.8.img",
            "filesize": 339525632,
            "id": "de1a2781-7d3f-4322-97d4-52fcd9df29c0",
            "links": {
                "download": "https://sandbox.zenodo.org/api/files/7b677fd2-2722-4f17-a270-3cef204f9858/art_2.5.8.img",
                "self": "https://sandbox.zenodo.org/api/deposit/depositions/960008/files/de1a2781-7d3f-4322-97d4-52fcd9df29c0",
            },
        }
    ],
    "id": 960008,
    "links": {
        "badge": "https://sandbox.zenodo.org/badge/doi/10.5072/zenodo.960008.svg",
        "bucket": "https://sandbox.zenodo.org/api/files/7b677fd2-2722-4f17-a270-3cef204f9858",
        "conceptbadge": "https://sandbox.zenodo.org/badge/doi/10.5072/zenodo.960007.svg",
        "conceptdoi": "https://doi.org/10.5072/zenodo.960007",
        "doi": "https://doi.org/10.5072/zenodo.960008",
        "latest": "https://sandbox.zenodo.org/api/records/960008",
        "latest_html": "https://sandbox.zenodo.org/record/960008",
        "record": "https://sandbox.zenodo.org/api/records/960008",
        "record_html": "https://sandbox.zenodo.org/record/960008",
    },
    "metadata": {
        "access_right": "open",
        "communities": [{"identifier": "zenodo"}],
        "creators": [{"affiliation": "Institut Pasteur", "name": "Cokelaer, Thomas"}],
        "description": 'Singularity image(s) of art software to be used and installed with damona\n(<a href="https://damona.readthedocs.org">See https://damona.readthedocs.org</a>) for reproducible bioinformatics\nanalysis.',
        "doi": "10.5072/zenodo.960008",
        "keywords": ["singularity", "damona", "bioinformatics", "reproducibility", "container"],
        "license": "CC-BY-4.0",
        "prereserve_doi": {"doi": "10.5072/zenodo.960008", "recid": 960008},
        "publication_date": "2021-11-13",
        "title": "Singularity image of art software",
        "upload_type": "physicalobject",
        "version": "v2.5.8",
    },
    "modified": "2021-11-13T20:22:57.340141+00:00",
    "owner": 18543,
    "record_id": 960008,
    "state": "done",
    "submitted": True,
    "title": "Singularity image of art software",
}


def make_zenodo(**kwargs):
    defaults = dict(token="dummy", affiliation="Institut Pasteur", author="Cokelaer, Thomas")
    defaults.update(kwargs)
    return zenodo.Zenodo("sandbox.zenodo", **defaults)


def test(mocker):
    mocker.patch("damona.zenodo.Zenodo.create_new_deposition", return_values={})

    try:
        z = zenodo.Zenodo("sandbox.zenodo")
    except:
        SystemExit

    z = make_zenodo()
    z.get_id(deposit)


def test_invalid_mode():
    with pytest.raises(AssertionError):
        zenodo.Zenodo("invalid.zenodo", token="t", author="a", affiliation="aff")


def test_headers():
    z = make_zenodo(token="mytoken")
    h = z.headers
    assert h["Authorization"] == "Bearer mytoken"
    assert h["Content-Type"] == "application/json"


def test_registry_name():
    z = make_zenodo()
    assert z.registry_name == "registry_sandbox.yaml"

    z2 = zenodo.Zenodo("zenodo", token="t", author="a", affiliation="aff")
    assert z2.registry_name == "registry.yaml"


def test_get_id_from_dict():
    z = make_zenodo()
    assert z.get_id({"id": 42}) == 42


def test_get_id_from_response():
    z = make_zenodo()
    mock_r = MagicMock()
    mock_r.json.return_value = {"id": 99}
    assert z.get_id(mock_r) == 99


def test_get_id_plain_int():
    z = make_zenodo()
    assert z.get_id(12345) == 12345


def test_get_id_from_deposit_fixture():
    z = make_zenodo()
    assert z.get_id(deposit) == 960008


def test_get_metadata_without_orcid():
    z = zenodo.Zenodo("sandbox.zenodo", token="dummy", affiliation="aff", author="A. Author")
    # Manually clear orcid to test the no-orcid branch regardless of local config
    z.orcid = None
    meta = z.get_metadata("fastqc", "0.11.9")
    m = meta["metadata"]
    assert "fastqc" in m["title"]
    assert m["version"] == "v0.11.9"
    assert m["upload_type"] == "physicalobject"
    creators = m["creators"]
    assert len(creators) == 1
    assert "orcid" not in creators[0]
    assert creators[0]["name"] == "A. Author"


def test_get_metadata_with_orcid():
    z = make_zenodo(orcid="0000-0001-2345-6789")
    meta = z.get_metadata("fastqc", "0.11.9")
    creator = meta["metadata"]["creators"][0]
    assert creator["orcid"] == "0000-0001-2345-6789"


def test_get_metadata_version_already_prefixed():
    z = make_zenodo()
    meta = z.get_metadata("fastqc", "v0.11.9")
    assert meta["metadata"]["version"] == "v0.11.9"


def test_orcid_url_stripped():
    z = make_zenodo(orcid="https://orcid.org/0000-0001-2345-6789")
    assert z.orcid == "0000-0001-2345-6789"


def test_orcid_invalid_format():
    with pytest.raises(SystemExit):
        make_zenodo(orcid="not-an-orcid")


def test_status_success():
    z = make_zenodo()
    mock_r = MagicMock()
    mock_r.status_code = 201
    z._status(mock_r, [201])
    assert mock_r in z.last_requests


def test_status_failure():
    z = make_zenodo()
    mock_r = MagicMock()
    mock_r.status_code = 403
    mock_r.reason = "FORBIDDEN"
    mock_r.json.return_value = {"message": "Permission denied."}
    with pytest.raises(SystemExit):
        z._status(mock_r, [201])


def test_print_info_new_deposit_unknown():
    z = make_zenodo()
    data = ImageName("fastqc_0.11.9.img")
    json_resp = {
        "id": 12345,
        "conceptdoi": "10.5281/zenodo.12344",
        "doi": "10.5281/zenodo.12345",
        "links": {"record_html": "https://zenodo.org/record/12345"},
        "files": [{"filename": "fastqc_0.11.9.img", "checksum": "abc123", "filesize": 1000}],
    }
    msg = z._print_info_new_deposit(data, json_resp, known=False)
    assert msg.startswith("fastqc:\n")
    assert "releases:" in msg
    assert "0.11.9:" in msg
    assert "abc123" in msg
    assert "10.5281/zenodo.12345" in msg


def test_print_info_new_deposit_known():
    z = make_zenodo()
    data = ImageName("fastqc_0.11.9.img")
    json_resp = {
        "id": 12345,
        "conceptdoi": "10.5281/zenodo.12344",
        "doi": "10.5281/zenodo.12345",
        "links": {"record_html": "https://zenodo.org/record/12345"},
        "files": [{"filename": "fastqc_0.11.9.img", "checksum": "abc123", "filesize": 1000}],
    }
    msg = z._print_info_new_deposit(data, json_resp, known=True)
    # known=True: no top-level software name block, just the release entry
    assert not msg.startswith("fastqc:")
    assert "0.11.9:" in msg
    assert "abc123" in msg


def test_get_stats_software_no_releases(mocker):
    mock_software = MagicMock()
    del mock_software.releases  # simulate missing attribute
    mocker.patch("damona.registry.Software", return_value=mock_software)
    assert zenodo.get_stats_software("unknown") == 0


def test_get_stats_software_no_zenodo_doi(mocker):
    mock_release = MagicMock()
    mock_release.doi = "biocontainers"
    mock_software = MagicMock()
    mock_software.releases = {"1.0.0": mock_release}
    mocker.patch("damona.registry.Software", return_value=mock_software)
    assert zenodo.get_stats_software("something") == 0


def test_get_stats_software_deduplication(mocker):
    """Old-style versioned records: all releases return same all_versions count → count once."""
    mock_release1 = MagicMock()
    mock_release1.doi = "10.5281/zenodo.1000"
    mock_release2 = MagicMock()
    mock_release2.doi = "10.5281/zenodo.1001"
    mock_software = MagicMock()
    mock_software.releases = {"1.0.0": mock_release1, "1.1.0": mock_release2}
    mocker.patch("damona.registry.Software", return_value=mock_software)
    mocker.patch("damona.zenodo.get_stats_id", return_value=4000)
    assert zenodo.get_stats_software("busco") == 4000


def test_get_stats_software_sum(mocker):
    """New-style independent deposits: each release has unique count → sum all."""
    mock_release1 = MagicMock()
    mock_release1.doi = "10.5281/zenodo.1000"
    mock_release2 = MagicMock()
    mock_release2.doi = "10.5281/zenodo.2000"
    mock_software = MagicMock()
    mock_software.releases = {"1.0.0": mock_release1, "2.0.0": mock_release2}
    mocker.patch("damona.registry.Software", return_value=mock_software)
    mocker.patch("damona.zenodo.get_stats_id", side_effect=[100, 200])
    assert zenodo.get_stats_software("isoquant") == 300


def test_get_stats_software_ignores_negative(mocker):
    """Releases that fail to fetch (return -1) are excluded from the sum."""
    mock_release1 = MagicMock()
    mock_release1.doi = "10.5281/zenodo.1000"
    mock_release2 = MagicMock()
    mock_release2.doi = "10.5281/zenodo.2000"
    mock_software = MagicMock()
    mock_software.releases = {"1.0.0": mock_release1, "2.0.0": mock_release2}
    mocker.patch("damona.registry.Software", return_value=mock_software)
    mocker.patch("damona.zenodo.get_stats_id", side_effect=[500, -1])
    assert zenodo.get_stats_software("something") == 500


def test_get_stat_id():
    from damona.zenodo import get_stats_id

    stats = get_stats_id("5708811")
    assert stats > 0


def test_get_stat_software():
    from damona.zenodo import get_stats_software

    stats = get_stats_software("fastqc")


def _mock_search_response(hits):
    response = MagicMock()
    response.status_code = 200
    response.headers = {}
    response.json.return_value = {"hits": {"hits": hits}}
    return response


def test_get_stats_records_batches(mocker):
    """A single batched request covers several record IDs."""
    hits = [
        {"id": 1000, "conceptrecid": "999", "stats": {"downloads": 50, "version_downloads": 30}},
        {"id": 1001, "conceptrecid": "999", "stats": {"downloads": 50, "version_downloads": 20}},
    ]
    mocked = mocker.patch("damona.zenodo.requests.get", return_value=_mock_search_response(hits))
    records = zenodo.get_stats_records(["1000", "1001"])
    assert mocked.call_count == 1
    assert records["1000"]["downloads"] == 50
    assert records["1001"]["conceptrecid"] == "999"


def test_get_stats_records_chunking(mocker):
    """More IDs than chunk_size triggers several requests."""
    mocked = mocker.patch("damona.zenodo.requests.get", return_value=_mock_search_response([]))
    zenodo.get_stats_records([str(x) for x in range(10)], chunk_size=4)
    assert mocked.call_count == 3


def test_get_stats_all_old_style_concept(mocker):
    """Old-style releases share one concept: its all-versions count is used once."""
    mock_release1 = MagicMock()
    mock_release1.doi = "10.5281/zenodo.1000"
    mock_release2 = MagicMock()
    mock_release2.doi = "10.5281/zenodo.1001"
    mock_software = MagicMock()
    mock_software.releases = {"1.0.0": mock_release1, "1.1.0": mock_release2}
    mocker.patch("damona.registry.Software", return_value=mock_software)
    records = {
        "1000": {"conceptrecid": "999", "downloads": 50, "version_downloads": 30},
        "1001": {"conceptrecid": "999", "downloads": 50, "version_downloads": 20},
    }
    mocker.patch("damona.zenodo.get_stats_records", return_value=records)
    totals = zenodo.get_stats_all(["busco"], use_cache=False)
    assert totals == {"busco": 50}


def test_get_stats_all_new_style_sum(mocker):
    """New-style independent deposits each have their own concept: counts sum up."""
    mock_release1 = MagicMock()
    mock_release1.doi = "10.5281/zenodo.1000"
    mock_release2 = MagicMock()
    mock_release2.doi = "10.5281/zenodo.2000"
    mock_software = MagicMock()
    mock_software.releases = {"1.0.0": mock_release1, "2.0.0": mock_release2}
    mocker.patch("damona.registry.Software", return_value=mock_software)
    records = {
        "1000": {"conceptrecid": "1000", "downloads": 100, "version_downloads": 100},
        "2000": {"conceptrecid": "2000", "downloads": 200, "version_downloads": 200},
    }
    mocker.patch("damona.zenodo.get_stats_records", return_value=records)
    totals = zenodo.get_stats_all(["isoquant"], use_cache=False)
    assert totals == {"isoquant": 300}


def test_get_stats_all_missing_record(mocker):
    """Records absent from the API response contribute zero, not an error."""
    mock_release = MagicMock()
    mock_release.doi = "10.5281/zenodo.1000"
    mock_software = MagicMock()
    mock_software.releases = {"1.0.0": mock_release}
    mocker.patch("damona.registry.Software", return_value=mock_software)
    mocker.patch("damona.zenodo.get_stats_records", return_value={})
    totals = zenodo.get_stats_all(["something"], use_cache=False)
    assert totals == {"something": 0}


def test_stats_cache_roundtrip(mocker, tmp_path):
    """Fresh cache is reused; stale cache is ignored."""
    cache_file = tmp_path / "stats_cache.json"
    mocker.patch("damona.zenodo._stats_cache_file", return_value=cache_file)

    records = {"1000": {"conceptrecid": "1000", "downloads": 5, "version_downloads": 5}}
    zenodo._save_stats_cache(records)
    assert zenodo._load_stats_cache() == records

    # stale cache must be dropped
    import json as _json

    data = _json.loads(cache_file.read_text())
    data["timestamp"] -= zenodo.STATS_CACHE_TTL + 1
    cache_file.write_text(_json.dumps(data))
    assert zenodo._load_stats_cache() == {}


def test_get_stats_all_uses_cache(mocker, tmp_path):
    """With a fresh cache, no request is made at all."""
    cache_file = tmp_path / "stats_cache.json"
    mocker.patch("damona.zenodo._stats_cache_file", return_value=cache_file)

    mock_release = MagicMock()
    mock_release.doi = "10.5281/zenodo.1000"
    mock_software = MagicMock()
    mock_software.releases = {"1.0.0": mock_release}
    mocker.patch("damona.registry.Software", return_value=mock_software)

    zenodo._save_stats_cache({"1000": {"conceptrecid": "1000", "downloads": 42, "version_downloads": 42}})
    mocked = mocker.patch("damona.zenodo.get_stats_records")
    totals = zenodo.get_stats_all(["fastqc"], use_cache=True)
    assert totals == {"fastqc": 42}
    assert mocked.call_count == 0


# ---------------------------------------------------------------------------
# stats helpers
# ---------------------------------------------------------------------------


def test_get_stats_headers_with_token(mocker):
    """A configured Zenodo token is turned into an Authorization header."""
    config = MagicMock()
    config.config.get.return_value = "ABC123"
    mocker.patch("damona.zenodo.Config", return_value=config)
    assert zenodo._get_stats_headers() == {"Authorization": "Bearer ABC123"}


def test_get_stats_headers_without_token(mocker):
    from configparser import NoOptionError

    config = MagicMock()
    config.config.get.side_effect = NoOptionError("token", "zenodo")
    mocker.patch("damona.zenodo.Config", return_value=config)
    assert zenodo._get_stats_headers() == {}


def test_sleep_if_rate_limited_no_headers():
    """Missing rate-limit headers must be a no-op."""
    response = MagicMock()
    response.headers = {}
    zenodo._sleep_if_rate_limited(response)


def test_sleep_if_rate_limited_quota_left():
    response = MagicMock()
    response.headers = {"X-RateLimit-Remaining": "10", "X-RateLimit-Reset": "0"}
    zenodo._sleep_if_rate_limited(response)


def test_sleep_if_rate_limited_waits(mocker):
    """When the quota is exhausted, we sleep until the reset time."""
    import time

    sleep = mocker.patch("time.sleep")
    response = MagicMock()
    response.headers = {
        "X-RateLimit-Remaining": "0",
        "X-RateLimit-Reset": str(int(time.time()) + 5),
    }
    zenodo._sleep_if_rate_limited(response)
    assert sleep.call_count == 1
    assert sleep.call_args[0][0] > 0


def test_load_stats_cache_missing_file(mocker, tmp_path):
    mocker.patch("damona.zenodo._stats_cache_file", return_value=tmp_path / "does_not_exist.json")
    assert zenodo._load_stats_cache() == {}


def test_load_stats_cache_corrupted(mocker, tmp_path):
    cache_file = tmp_path / "stats_cache.json"
    cache_file.write_text("{not json")
    mocker.patch("damona.zenodo._stats_cache_file", return_value=cache_file)
    assert zenodo._load_stats_cache() == {}


def test_get_stats_id_special_values():
    assert zenodo.get_stats_id("bioconainers") == 0
    assert zenodo.get_stats_id(None, name="fastqc") == 0


def test_get_stats_id_bad_answer(mocker):
    """A malformed Zenodo answer returns -1 rather than raising."""
    response = MagicMock()
    response.headers = {}
    response.json.return_value = {}
    mocker.patch("requests.get", return_value=response)
    assert zenodo.get_stats_id(123456) == -1


def test_stats_cache_file_location():
    """The stats cache lives next to damona.cfg."""
    path = zenodo._stats_cache_file()
    assert path.name == "stats_cache.json"


def test_get_stats_all_default_softwares(mocker, tmp_path):
    """Without an explicit list, get_stats_all covers the whole registry."""
    mocker.patch("damona.zenodo._stats_cache_file", return_value=tmp_path / "stats_cache.json")
    mocker.patch("damona.admin.get_software_names", return_value={"fastqc"})

    mock_release = MagicMock()
    mock_release.doi = "10.5281/zenodo.1000"
    mock_software = MagicMock()
    mock_software.releases = {"1.0.0": mock_release}
    mocker.patch("damona.registry.Software", return_value=mock_software)

    mocker.patch(
        "damona.zenodo.get_stats_records",
        return_value={"1000": {"conceptrecid": "1000", "downloads": 7, "version_downloads": 7}},
    )
    totals = zenodo.get_stats_all(use_cache=True)
    assert totals == {"fastqc": 7}
    # the answer has been cached for the next call
    assert zenodo._load_stats_cache()["1000"]["downloads"] == 7
