import builtins

import mock
import pytest
from click.testing import CliRunner

from damona import Damona, Environ, script
from damona.install import LocalImageInstaller, RemoteURLInstaller

from . import test_dir


def test_cmd():
    from damona.install import CMD

    c = CMD(["damona", "install"])
    c.__repr__()


def test_remote_url_installer_binary_inference():
    """Test that RemoteURLInstaller correctly infers binary names from URLs."""
    # Binary name inferred from filename
    inst = RemoteURLInstaller("https://example.com/fastqc_0.11.9.img")
    assert inst.binaries == ["fastqc"]

    # Binary name provided via name argument
    inst2 = RemoteURLInstaller("https://example.com/fastqc_0.11.9.img", name="myfastqc")
    assert inst2.binaries == ["myfastqc"]

    # Binary names provided via binaries list (overrides name)
    inst3 = RemoteURLInstaller("https://example.com/fastqc_0.11.9.img", binaries=["fastqc", "fastqc2"])
    assert inst3.binaries == ["fastqc", "fastqc2"]

    # Version with 'v' prefix
    inst4 = RemoteURLInstaller("https://example.com/samtools_v1.12.0.img")
    assert inst4.binaries == ["samtools"]


def test_remote_url_installer_invalid_filename():
    """Test that RemoteURLInstaller exits when binary name cannot be inferred."""
    with pytest.raises(SystemExit):
        RemoteURLInstaller("https://example.com/myimage.img")


def test_install_direct_url_routing(monkeypatch):
    """Test that install command routes direct URLs to RemoteURLInstaller."""
    captured = {}

    class FakeRemoteURLInstaller:
        def __init__(self, url, name=None, binaries=None, cmd=None):
            captured["url"] = url
            captured["name"] = name
            captured["binaries"] = binaries
            self.image_installed = True

        def is_valid(self):
            return True

        def pull_image(self, force=False):
            pass

        def install_binaries(self, force=False):
            pass

    monkeypatch.setattr("damona.script.RemoteURLInstaller", FakeRemoteURLInstaller)

    runner = CliRunner()
    NAME = "damona__testing__install_direct_url"
    Setup(NAME)
    manager = Damona()
    monkeypatch.setenv("DAMONA_ENV", str(manager.damona_path / "envs" / NAME))

    result = runner.invoke(script.install, ["https://example.com/fastqc_0.11.9.img"])
    assert result.exit_code == 0
    assert captured.get("url") == "https://example.com/fastqc_0.11.9.img"
    assert captured.get("name") is None  # No name provided for direct URL

    Teardown(NAME)


def test_install_from_url_option_routing(monkeypatch):
    """Test that --from-url option routes to RemoteURLInstaller with correct name."""
    captured = {}

    class FakeRemoteURLInstaller:
        def __init__(self, url, name=None, binaries=None, cmd=None):
            captured["url"] = url
            captured["name"] = name
            captured["binaries"] = binaries
            self.image_installed = True

        def is_valid(self):
            return True

        def pull_image(self, force=False):
            pass

        def install_binaries(self, force=False):
            pass

    monkeypatch.setattr("damona.script.RemoteURLInstaller", FakeRemoteURLInstaller)

    runner = CliRunner()
    NAME = "damona__testing__install_from_url"
    Setup(NAME)
    manager = Damona()
    monkeypatch.setenv("DAMONA_ENV", str(manager.damona_path / "envs" / NAME))

    result = runner.invoke(
        script.install,
        ["fastqc", "--from-url", "https://example.com/fastqc_0.11.9.img"],
    )
    assert result.exit_code == 0
    assert captured.get("url") == "https://example.com/fastqc_0.11.9.img"
    assert captured.get("name") == "fastqc"

    Teardown(NAME)


def test_ImageInstaller(monkeypatch):

    runner = CliRunner()
    NAME = "damona__testing__install_ImageInstaller"
    Setup(NAME)
    manager = Damona()
    monkeypatch.setenv("DAMONA_ENV", str(manager.damona_path / "envs" / NAME))

    # This re-installs the image, interfering with the user's local image but should be safe
    results = runner.invoke(script.install, [f"{test_dir}/data/testing_1.0.0.img", "--binaries", "hello", "--force"])
    assert results.exit_code == 0

    # This will fail because hello2 is not in the image
    results = runner.invoke(script.install, [f"{test_dir}/data/testing_1.0.0.img", "--binaries", "hello2", "--force"])
    assert results.exit_code == 1

    # Fails because file does not exist
    results = runner.invoke(script.install, [f"{test_dir}/data/testing_2.0.0.img", "--binaries", "hello2", "--force"])
    assert results.exit_code == 1

    # and not a directory
    results = runner.invoke(script.install, [f"{test_dir}/data", "--binaries", "hello2", "--force"])
    assert results.exit_code == 1

    Teardown(NAME)


def Teardown(NAME):
    runner = CliRunner()
    with mock.patch.object(builtins, "input", lambda _: "y"):
        results = runner.invoke(script.delete, [NAME])
        assert results.exit_code == 0


def Setup(NAME):
    runner = CliRunner()
    if NAME not in Environ().environment_names:

        results = runner.invoke(script.create, [NAME, "--force"])

        assert results.exit_code == 0
