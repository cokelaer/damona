import builtins
import subprocess

import mock
import pytest
from click.testing import CliRunner

from damona import Config, Damona, Environ, script

from . import test_dir


def test_damon_builder_docker(tmpdir):
    directory = tmpdir.mkdir("images")
    destination = directory / "alpine_1.0.0.img"
    from click.testing import CliRunner

    runner = CliRunner()

    results = runner.invoke(script.build, ["docker://alpine", " --destination", destination])
    # assert results.exit_code == 0


def test_damona_version():
    cmd = "damona --version"
    status = subprocess.call(cmd.split())
    assert status == 0


def test_activate_deactivate_bash(monkeypatch):

    NAME = "damona__testing__deactivate_bash"
    Setup(NAME)
    manager = Damona()
    monkeypatch.setenv("DAMONA_ENV", str(manager.damona_path / "envs" / NAME))
    runner = CliRunner()
    results = runner.invoke(script.activate, [NAME])
    assert results.exit_code == 0
    results = runner.invoke(script.deactivate, [NAME])
    assert results.exit_code == 0
    Teardown(NAME)


def test_activate_deactivate_fish(monkeypatch, mocker):

    NAME = "damona__testing__deactivate_fish"

    Setup(NAME)
    mocker.patch("damona.environ.Environ._is_fish_shell", return_values=True)

    manager = Damona()
    monkeypatch.setenv("DAMONA_ENV", str(manager.damona_path / "envs" / NAME))
    runner = CliRunner()
    results = runner.invoke(script.activate, [NAME])
    assert results.exit_code == 0
    results = runner.invoke(script.deactivate, [NAME])
    assert results.exit_code == 0
    Teardown(NAME)


def test_damona_clean():
    runner = CliRunner()
    results = runner.invoke(script.clean, [])
    assert results.exit_code == 0


def test_damona_info():
    runner = CliRunner()
    results = runner.invoke(script.info, ["base"])
    assert results.exit_code == 0

    results = runner.invoke(script.info, ["__dummy__yummy__"])
    assert results.exit_code == 1


def test_damona_create_and_install(monkeypatch):
    NAME = "damona__testing__create_and_install"
    Setup(NAME)

    manager = Damona()
    monkeypatch.setenv("DAMONA_ENV", str(manager.damona_path / "envs" / NAME))

    runner = CliRunner()
    results = runner.invoke(script.install, ["fastqc"])
    assert results.exit_code == 0

    results = runner.invoke(script.install, ["fastqc", "--force"])
    assert results.exit_code == 0

    Teardown(NAME)


def test_create():
    runner = CliRunner()
    results = runner.invoke(script.env, ["--create", "test_create", "--delete", "test"])


def test_env():

    # list the packages
    runner = CliRunner()
    results = runner.invoke(script.env, [])
    assert results.exit_code == 0

    # create damona__testing__ env

    NAME = "damona__testing__env"
    Setup(NAME)

    # delete it
    import mock

    with mock.patch.object(builtins, "input", lambda _: "y"):
        results = runner.invoke(script.env, [])
        assert results.exit_code == 0

    assert results.exit_code == 0

    Teardown(NAME)


def test_search():
    runner = CliRunner()
    results = runner.invoke(script.search, [])
    assert results.exit_code == 2

    results = runner.invoke(script.search, ["*"])
    assert results.exit_code == 0

    results = runner.invoke(script.search, ["fastqc"])
    assert results.exit_code == 0

    results = runner.invoke(script.search, ["fastqc", "--binaries-only"])
    assert results.exit_code == 0

    results = runner.invoke(script.search, ["fastqc", "--registry", "damona"])
    assert results.exit_code == 0


def test_list():
    runner = CliRunner()
    results = runner.invoke(script.list, [])
    assert results.exit_code == 0


def test_stats():
    runner = CliRunner()
    results = runner.invoke(script.stats, [])
    assert results.exit_code == 0


def test_export(monkeypatch, tmpdir):
    directory = tmpdir.mkdir("output")

    runner = CliRunner()

    NAME = "damona__testing__export"
    Setup(NAME)

    manager = Damona()
    monkeypatch.setenv("DAMONA_ENV", str(manager.damona_path / "envs" / NAME))

    results = runner.invoke(script.export, [NAME, "--bundle", directory / "test.tar"])
    assert results.exit_code == 0

    results = runner.invoke(script.export, [NAME, "--yaml", directory / "test.yaml"])
    assert results.exit_code == 0

    Teardown(NAME)


def test_import_bundle(monkeypatch, tmpdir):
    directory = tmpdir.mkdir("output")
    output = directory / "test.tar"
    manager = Damona()
    runner = CliRunner()

    NAME = "damona__testing__import_bundle"
    NAME2 = "damona__testing__import_bundle2"
    Setup(NAME)

    monkeypatch.setenv("DAMONA_ENV", str(manager.damona_path / "envs" / NAME))
    results = runner.invoke(script.install, ["fastqc"])
    results = runner.invoke(script.export, [NAME, "--output", output])
    results = runner.invoke(script.create, [NAME2, "--from-bundle", output])

    # suppress this temporary environment
    with mock.patch.object(builtins, "input", lambda _: "y"):
        results = runner.invoke(script.delete, [NAME2])
        assert results.exit_code == 0

    # supress the damona__testing__ temporary environment
    Teardown(NAME)


def Teardown(name):
    runner = CliRunner()
    with mock.patch.object(builtins, "input", lambda _: "y"):
        results = runner.invoke(script.delete, [name])
        assert results.exit_code == 0


def Setup(name):
    runner = CliRunner()
    if name not in Environ().environment_names:
        results = runner.invoke(script.create, [name])
        assert results.exit_code == 0


def test_install_remove(monkeypatch):
    runner = CliRunner()

    NAME = "damona__testing__install_remove"
    Setup(NAME)
    manager = Damona()
    monkeypatch.setenv("DAMONA_ENV", str(manager.damona_path / "envs" / NAME))

    results = runner.invoke(script.install, ["fastqc"])
    assert results.exit_code == 0
    results = runner.invoke(script.remove, ["fastqc"])
    assert results.exit_code == 0

    Teardown(NAME)


def test_install_remove_from_url(monkeypatch):
    runner = CliRunner()

    NAME = "damona__testing__install_remove_from_url"
    Setup(NAME)
    manager = Damona()
    monkeypatch.setenv("DAMONA_ENV", str(manager.damona_path / "envs" / NAME))

    # This re-installs the image, interfering with the user's local image but should be safe
    results = runner.invoke(script.install, ["fastqc", "--registry", "damona", "--force"])
    assert results.exit_code == 0

    Teardown(NAME)


def test_install_local(monkeypatch):

    NAME = "damona__testing__install_local"
    Setup(NAME)
    manager = Damona()
    monkeypatch.setenv("DAMONA_ENV", str(manager.damona_path / "envs" / NAME))

    # This re-installs the image, interfering with the user's local image but should be safe
    runner = CliRunner()
    results = runner.invoke(script.install, [f"{test_dir}/data/testing_1.0.0.img", "--binaries", "hello"])
    assert results.exit_code == 0
    results = runner.invoke(script.install, [f"{test_dir}/data/testing_1.0.0.img", "--binaries", "hello", "--force"])
    assert results.exit_code == 0

    Teardown(NAME)


def test_install_biocontainers(monkeypatch):

    NAME = "damona__testing__install_biocontainers"
    Setup(NAME)
    manager = Damona()
    monkeypatch.setenv("DAMONA_ENV", str(manager.damona_path / "envs" / NAME))

    # This re-installs the image, interfering with the user's local image but should be safe
    runner = CliRunner()
    results = runner.invoke(script.install, [f"biocontainers/hisat2:2.2.1"])
    assert results.exit_code == 0

    Teardown(NAME)
