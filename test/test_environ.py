import os
import builtins
import mock

from damona.environ import Environment
from damona.environ import Environ
from damona import Damona
from damona import script
import damona
from click.testing import CliRunner
import subprocess

def test_no_var(monkeypatch):
    monkeypatch.delenv("DAMONA_ENV", raising=False)
    try:
        Environ()
        assert False
    except:
        assert True


def test_environ(monkeypatch):
    manager = Damona()
    env = Environ()
    env.N
    env.environments
    env.create(".dummy_test")
    import mock

    with mock.patch.object(builtins, "input", lambda _: "y"):
        env.delete(".dummy_test")

    env.environment_names

    # this only prints the new PATH on the screen, so we need ti monkey patch the real env
    env.activate("base")
    monkeypatch.setenv("DAMONA_ENV", str(manager.damona_path / "envs" / "base"))
    assert env.get_current_env_name() == "base"
    env.deactivate()


def test_environment_no_var(monkeypatch):
    monkeypatch.delenv("DAMONA_PATH", raising=False)
    e = Environment("base")
    try:
        e.get_disk_usage()
        assert False
    except:
        assert True


def test_environment():
    e = Environment("base")
    e.get_installed_binaries()
    e.get_current_state()
    # cannot rename the base
    try:
        e.rename("base")
        assert False
    except SystemExit:
        assert True

    try:
        e = Environment("base_does_not_exist")
        assert False
    except:
        assert True

    env = Environ()
    env.create(".dummy_test")
    with mock.patch.object(builtins, "input", lambda _: "y"):
        this_env = Environment(".dummy_test")
        try:
            # cannot rename with existing  name
            this_env.rename(".dummy_test")
            assert False
        except SystemExit:
            assert True
        # cleanup
        env.delete(".dummy_test")



def test_create_bundle(tmpdir, monkeypatch):
    # make sure it exists
    runner = CliRunner()

    if "damona__testing__" not in Environ().environment_names:
        results = runner.invoke(script.env, ["--create", "damona__testing__"])

    manager = Damona()
    monkeypatch.setenv("DAMONA_ENV", str(manager.damona_path / "envs/damona__testing__"))
    cmd = "damona install fastqc --force"
    status = subprocess.call(cmd.split())


    directory = tmpdir.mkdir("bundle")
    destination = directory / "test"
    #print(destination)
    e = Environment("damona__testing__")
    e.create_bundle()
    os.remove("damona_damona__testing__.tar")

    # cleanup
    with mock.patch.object(builtins, "input", lambda _: "y"):
        results = runner.invoke(script.env, ["--delete", "damona__testing__"])







