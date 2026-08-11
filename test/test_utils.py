import pytest
import requests

from damona.utils import download_with_progress


def test_download(tmpdir):

    directory = tmpdir.mkdir("images")
    destination = directory / "test_1.0.0.img"
    download_with_progress("https://zenodo.org/record/7817800/files/minimap2_2.24.0.img", destination)


def test_download_bad_status(mocker, tmpdir):
    """A non-200 answer must raise instead of writing a corrupted file."""

    class _Response:
        status_code = 404

        def raise_for_status(self):
            raise requests.HTTPError("404 Not Found")

    mocker.patch("requests.get", return_value=_Response())
    destination = tmpdir.mkdir("images") / "test_1.0.0.img"
    with pytest.raises(requests.HTTPError):
        download_with_progress("https://example.org/whatever.img", destination)
    assert not destination.exists()
