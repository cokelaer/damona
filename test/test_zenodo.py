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
