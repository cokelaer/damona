from damona import script
import subprocess
import pytest


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


def test_damona_env():
    from click.testing import CliRunner

    runner = CliRunner()

    results = runner.invoke(script.env, [])
    assert results.exit_code == 0



def test_damona_create_and_export(monkeypatch):

    from damona import Config
    from damona import Damona

    manager = Damona()

    cmd = "damona env --create damona__testing__"
    status = subprocess.call(cmd.split())
    assert status == 0

    monkeypatch.setenv("DAMONA_ENV", manager.damona_path / "envs/damona__testing__")
    cmd = "damona install fastqc"
    status = subprocess.call(cmd.split())
    assert status == 0
