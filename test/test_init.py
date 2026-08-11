"""Tests for the damona top-level package helpers."""

import requests

from damona import check_for_updates, get_package_version


def test_get_package_version_found():
    assert get_package_version("damona") != "damona not found"


def test_get_package_version_not_found():
    assert get_package_version("this_package_does_not_exist_xyz") == "this_package_does_not_exist_xyz not found"


class _Response:
    def __init__(self, version="99.99.99"):
        self._version = version

    def raise_for_status(self):
        pass

    def json(self):
        return {"info": {"version": self._version}}


def test_check_for_updates_newer_available(mocker, caplog):
    mocker.patch("requests.get", return_value=_Response("99.99.99"))
    check_for_updates("damona", "0.0.1")


def test_check_for_updates_up_to_date(mocker):
    mocker.patch("requests.get", return_value=_Response("0.0.1"))
    check_for_updates("damona", "0.0.1")


def test_check_for_updates_no_connection(mocker):
    mocker.patch("requests.get", side_effect=requests.ConnectionError)
    check_for_updates("damona", "0.0.1")


def test_check_for_updates_timeout(mocker):
    mocker.patch("requests.get", side_effect=requests.Timeout)
    check_for_updates("damona", "0.0.1")


def test_check_for_updates_request_exception(mocker):
    mocker.patch("requests.get", side_effect=requests.RequestException("boom"))
    check_for_updates("damona", "0.0.1")
