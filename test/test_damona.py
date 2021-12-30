import builtins
import subprocess
from damona import script
from damona import Config
from damona import Damona
from damona import Environ
import pytest
from click.testing import CliRunner
import mock

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
    setup(NAME)
    manager = Damona()
    monkeypatch.setenv("DAMONA_ENV", str(manager.damona_path / "envs" / NAME ))
    runner = CliRunner()
    results = runner.invoke(script.activate, [NAME])
    assert results.exit_code == 0
    results = runner.invoke(script.deactivate, [NAME])
    assert results.exit_code == 0
    teardown(NAME)

def test_activate_deactivate_fish(monkeypatch, mocker):

    NAME = "damona__testing__deactivate_fish"

    setup(NAME)
    mocker.patch("damona.environ.Environ._is_fish_shell", return_values=True)

    manager = Damona()
    monkeypatch.setenv("DAMONA_ENV", str(manager.damona_path / "envs" /  NAME))
    runner = CliRunner()
    results = runner.invoke(script.activate, [NAME])
    assert results.exit_code == 0
    results = runner.invoke(script.deactivate, [NAME])
    assert results.exit_code == 0
    teardown(NAME)


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
    setup(NAME)

    manager = Damona()


    monkeypatch.setenv("DAMONA_ENV", str(manager.damona_path / "envs" / NAME))
    cmd = "damona install fastqc"
    status = subprocess.call(cmd.split())
    assert status == 0
    cmd = "damona install fastqc --force"
    status = subprocess.call(cmd.split())
    assert status == 0

    teardown(NAME)

def test_env():

    # list the packages
    runner = CliRunner()
    results = runner.invoke(script.env, [])
    assert results.exit_code == 0

    # diskusage
    runner = CliRunner()
    results = runner.invoke(script.env, ["--disk-usage"])
    assert results.exit_code == 0

    # wrong arguments mutually exclusive
    runner = CliRunner()
    results = runner.invoke(script.env, ["--create", "test", "--delete" , "test"])
    assert results.exit_code == 1
    results = runner.invoke(script.env, ["--create", "test", "--rename" , "test"])
    assert results.exit_code == 1
    results = runner.invoke(script.env, ["--rename", "test", "--delete" , "test"])
    assert results.exit_code == 1

    # create damona__testing__ env

    NAME = "damona__testing__env"
    setup(NAME)

    # delete it
    import mock
    with mock.patch.object(builtins, "input", lambda _: "y"):
        results = runner.invoke(script.env, ["--delete", NAME])
        assert results.exit_code == 0

    # and install again
    results = runner.invoke(script.env, ["--create", NAME])
    assert results.exit_code == 0

    with mock.patch.object(builtins, "input", lambda _: ""):
        results = runner.invoke(script.env, ["--rename", NAME])
        assert results.exit_code == 1
        results = runner.invoke(script.env, ["--rename", NAME, 
            "--new-name", NAME+"new"])
        assert results.exit_code == 0

    results = runner.invoke(script.env, ["--rename", NAME + "new", 
        "--new-name", NAME, "--force"])
    assert results.exit_code == 0

    teardown(NAME)

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

    results = runner.invoke(script.search, ["fastqc", "--url", "damona"])
    assert results.exit_code == 0

def test_list():
    runner = CliRunner()
    results = runner.invoke(script.list, [])
    assert results.exit_code == 0

def test_stats():
    runner = CliRunner()
    results = runner.invoke(script.stats, [])
    assert results.exit_code == 0


def test_export():
    runner = CliRunner()

    NAME = "damona__testing__export"
    setup(NAME)

    results = runner.invoke(script.export, [NAME])
    assert results.exit_code == 0

    teardown(NAME)

def test_import_bundle(monkeypatch):
    manager = Damona()
    runner = CliRunner()

    NAME="damona__testing__import_bundle"
    NAME2="damona__testing__import_bundle2"
    setup(NAME)

    monkeypatch.setenv("DAMONA_ENV", str(manager.damona_path / "envs" / NAME))
    results = runner.invoke(script.install, ["fastqc"])
    results = runner.invoke(script.export, [NAME])
    results = runner.invoke(script.env, ["--create", NAME2, 
        "--from-bundle", "damona_damona__testing__.tar"])

    # suppress this temporary environment
    with mock.patch.object(builtins, "input", lambda _: "y"):
        results = runner.invoke(script.env, ["--delete", NAME2])
        assert results.exit_code == 0

    # supress the damona__testing__ temporary environment
    teardown(NAME)

def teardown(name="damona__testing__"):
    runner = CliRunner()
    with mock.patch.object(builtins, "input", lambda _: "y"):
        results = runner.invoke(script.env, ["--delete", name])
        assert results.exit_code == 0



def setup(name="damona__testing__"):
    runner = CliRunner()
    if name not in Environ().environment_names:
        results = runner.invoke(script.env, ["--create", name])
        assert results.exit_code == 0



def test_install_remove(monkeypatch):
    runner = CliRunner()

    NAME = "damona__testing__install_remove"
    setup(NAME)
    manager = Damona()
    monkeypatch.setenv("DAMONA_ENV", str(manager.damona_path / "envs" / NAME))

    results = runner.invoke(script.install, ["fastqc"])
    assert results.exit_code == 0
    results = runner.invoke(script.remove, ["fastqc"])
    assert results.exit_code == 0

    teardown(NAME)


def test_install_remove_from_url(monkeypatch):
    runner = CliRunner()

    NAME = "damona__testing__install_remove_from_url"
    setup(NAME)
    manager = Damona()
    monkeypatch.setenv("DAMONA_ENV", str(manager.damona_path / "envs" / NAME))

    # This re-installs the image, interfering with the user's local image but should be safe
    results = runner.invoke(script.install, ["fastqc", "--url", "damona", "--force"])
    assert results.exit_code == 0

    teardown(NAME)


def test_install_local(monkeypatch):
    runner = CliRunner()

    NAME = "damona__testing__install_local"
    setup(NAME)
    manager = Damona()
    monkeypatch.setenv("DAMONA_ENV", str(manager.damona_path / "envs" / NAME ))

    # This re-installs the image, interfering with the user's local image but should be safe
    results = runner.invoke(script.install, [f"{test_dir}/data/testing_1.0.0.img", "--binaries", "hello", "--force"])


    assert results.exit_code == 0

    teardown(NAME)









