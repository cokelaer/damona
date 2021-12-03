import builtins
import subprocess
from damona import script
from damona import Config
from damona import Damona
from damona import Environ
import pytest
from click.testing import CliRunner
import mock


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


def test_activate_deactivate(monkeypatch):
    setup()
    manager = Damona()
    monkeypatch.setenv("DAMONA_ENV", str(manager.damona_path / "envs/damona__testing__"))
    runner = CliRunner()
    results = runner.invoke(script.activate, ["damona__testing__"])
    assert results.exit_code == 0
    results = runner.invoke(script.deactivate, ["damona__testing__"])
    assert results.exit_code == 0

    teardown()

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


def test_damona_create_and_export(monkeypatch):
    manager = Damona()

    # make sure it exists
    runner = CliRunner()
    results = runner.invoke(script.env, ["--create", "damona__testing__"])
    assert results.exit_code == 0

    monkeypatch.setenv("DAMONA_ENV", str(manager.damona_path / "envs/damona__testing__"))
    cmd = "damona install fastqc"
    status = subprocess.call(cmd.split())
    assert status == 0
    cmd = "damona install fastqc --force"
    status = subprocess.call(cmd.split())
    assert status == 0

def test_env():
    setup()

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

    # make sure it exists
    results = runner.invoke(script.env, ["--create", "damona__testing__"])
    assert results.exit_code == 0

    # delete it
    import mock
    with mock.patch.object(builtins, "input", lambda _: "y"):
        results = runner.invoke(script.env, ["--delete", "damona__testing__"])
        assert results.exit_code == 0

    # and install again
    results = runner.invoke(script.env, ["--create", "damona__testing__"])
    assert results.exit_code == 0

    with mock.patch.object(builtins, "input", lambda _: ""):
        results = runner.invoke(script.env, ["--rename", "damona__testing__"])
        assert results.exit_code == 1
        results = runner.invoke(script.env, ["--rename", "damona__testing__", 
            "--new-name", "damona__testing__new"])
        assert results.exit_code == 0

    results = runner.invoke(script.env, ["--rename", "damona__testing__new", 
        "--new-name", "damona__testing__", "--force"])
    assert results.exit_code == 0

    teardown()

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


def test_stats():
    runner = CliRunner()
    results = runner.invoke(script.stats, [])
    assert results.exit_code == 0


def test_export():
    runner = CliRunner()

    if "damona__testing__" not in Environ().environment_names:
        results = runner.invoke(script.env, ["--create", "damona__testing__"])
        assert results.exit_code == 0

    results = runner.invoke(script.export, ["damona__testing__"])
    assert results.exit_code == 0

def test_import_bundle(monkeypatch):
    manager = Damona()
    runner = CliRunner()

    setup()

    monkeypatch.setenv("DAMONA_ENV", str(manager.damona_path / "envs/damona__testing__"))
    results = runner.invoke(script.install, ["fastqc"])
    results = runner.invoke(script.export, ["damona__testing__"])
    results = runner.invoke(script.env, ["--create","damona__testing2__", 
        "--from-bundle", "damona_damona__testing__.tar"])

    teardown()

def teardown():
    runner = CliRunner()
    with mock.patch.object(builtins, "input", lambda _: "y"):
        results = runner.invoke(script.env, ["--delete", "damona__testing__"])
        assert results.exit_code == 0

    with mock.patch.object(builtins, "input", lambda _: "y"):
        results = runner.invoke(script.env, ["--delete", "damona__testing2__"])
        assert results.exit_code == 0


def setup():
    runner = CliRunner()
    if "damona__testing__" not in Environ().environment_names:
        results = runner.invoke(script.env, ["--create", "damona__testing__"])
        assert results.exit_code == 0
