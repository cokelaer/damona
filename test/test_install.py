import builtins

import mock
import pytest
from click.testing import CliRunner

from damona import Damona, Environ, script
from damona.install import LocalImageInstaller

from . import test_dir


def test_cmd():
    from damona.install import CMD

    c = CMD(["damona", "install"])
    c.__repr__()


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
        results = runner.invoke(script.remove, [NAME])
        assert results.exit_code == 0


def Setup(NAME):
    runner = CliRunner()
    if NAME not in Environ().environment_names:

        results = runner.invoke(script.create, [NAME, "--force"])

        assert results.exit_code == 0


# ---------------------------------------------------------------------------
# ImageInstaller.install_binaries when image not installed (line 134)
# ---------------------------------------------------------------------------


def test_local_image_installer_no_binaries():
    """LocalImageInstaller guesses the binary name from the image filename (line 175)."""
    from damona.install import LocalImageInstaller

    lii = LocalImageInstaller(f"{test_dir}/data/testing_1.0.0.img")
    # binary is guessed from the image stem: "testing_1.0.0" → "testing"
    assert lii.binaries == [lii.input_image.guessed_executable]
    assert len(lii.binaries) == 1


def test_install_binaries_image_not_installed():
    """install_binaries logs critical and returns when image_installed is False."""
    from damona.install import LocalImageInstaller

    lii = LocalImageInstaller.__new__(LocalImageInstaller)
    lii.image_installed = False
    lii.binaries = ["hello"]
    # Should not raise – just logs a critical message
    lii.install_binaries()


# ---------------------------------------------------------------------------
# BinaryInstaller with env_name argument (lines 552-554)
# ---------------------------------------------------------------------------


def test_binary_installer_env_name(monkeypatch):
    """BinaryInstaller resolves env_name to a filesystem path."""
    import shutil

    from damona import Damona
    from damona.install import BinaryInstaller

    NAME = "damona__testing__install__bi_env_name"
    runner = CliRunner()
    Setup(NAME)
    manager = Damona()

    try:
        bi = BinaryInstaller(["hello"], f"{test_dir}/data/testing_1.0.0.img", env_name=NAME)
        assert str(bi.env_name) == str(manager.environments_path / NAME)
    finally:
        Teardown(NAME)


# ---------------------------------------------------------------------------
# BinaryInstaller: existing binary without --force logs warning (lines 594-596)
# ---------------------------------------------------------------------------


def test_binary_installer_existing_no_force(monkeypatch):
    """Installing a binary that already exists without force logs a warning."""
    import shutil

    from damona import Damona
    from damona.install import BinaryInstaller

    NAME = "damona__testing__install__bi_existing_no_force"
    manager = Damona()
    Setup(NAME)
    monkeypatch.setenv("DAMONA_ENV", str(manager.damona_path / "envs" / NAME))

    try:
        bi = BinaryInstaller(["hello"], f"{test_dir}/data/testing_1.0.0.img")
        bi.install_binaries(force=True)  # first install
        bi2 = BinaryInstaller(["hello"], f"{test_dir}/data/testing_1.0.0.img")
        bi2.install_binaries(force=False)  # second call without force → warning, no overwrite
        # Binary still present
        assert (manager.environments_path / NAME / "bin" / "hello").exists()
    finally:
        Teardown(NAME)
