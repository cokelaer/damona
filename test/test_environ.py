import builtins
import os
import subprocess

import mock
from click.testing import CliRunner

import damona
from damona import Damona, script
from damona.environ import Environ, Environment


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
    env.create(".dummy_test2")
    with mock.patch.object(builtins, "input", lambda _: "y"):
        this_env = Environment(".dummy_test2")
        try:
            # cannot rename with existing  name
            this_env.rename(".dummy_test2")
            assert False
        except SystemExit:
            assert True
        # cleanup
        env.delete(".dummy_test2")

    try:
        env = Environ()
        env.create("base")
        assert False
    except SystemExit:
        assert True

    env._is_bash_shell()
    env._is_fish_shell()


def test_detect_shell(monkeypatch):
    env = Environ()

    # DAMONA_SHELL_INFO takes priority
    monkeypatch.setenv("DAMONA_SHELL_INFO", "fish")
    assert env._detect_shell() == "fish"
    assert env._is_fish_shell() is True
    assert env._is_bash_shell() is False
    assert env._is_zsh_shell() is False

    monkeypatch.setenv("DAMONA_SHELL_INFO", "bash")
    assert env._detect_shell() == "bash"
    assert env._is_bash_shell() is True

    monkeypatch.setenv("DAMONA_SHELL_INFO", "zsh")
    assert env._detect_shell() == "zsh"
    assert env._is_zsh_shell() is True

    # Without DAMONA_SHELL_INFO, fall back to shell-specific variables
    monkeypatch.delenv("DAMONA_SHELL_INFO", raising=False)

    monkeypatch.setenv("FISH_VERSION", "3.6.0")
    monkeypatch.delenv("ZSH_VERSION", raising=False)
    monkeypatch.delenv("BASH_VERSION", raising=False)
    assert env._detect_shell() == "fish"
    assert env._is_fish_shell() is True

    monkeypatch.delenv("FISH_VERSION", raising=False)
    monkeypatch.setenv("ZSH_VERSION", "5.9")
    assert env._detect_shell() == "zsh"
    assert env._is_zsh_shell() is True

    monkeypatch.delenv("ZSH_VERSION", raising=False)
    monkeypatch.setenv("BASH_VERSION", "5.1.0")
    assert env._detect_shell() == "bash"
    assert env._is_bash_shell() is True

    # Without version variables, fall back to $SHELL
    monkeypatch.delenv("BASH_VERSION", raising=False)
    monkeypatch.setenv("SHELL", "/usr/bin/fish")
    assert env._detect_shell() == "fish"

    monkeypatch.setenv("SHELL", "/bin/zsh")
    assert env._detect_shell() == "zsh"

    monkeypatch.setenv("SHELL", "/bin/bash")
    assert env._detect_shell() == "bash"

    # Unknown shell returns empty string
    monkeypatch.setenv("SHELL", "/bin/sh")
    assert env._detect_shell() == ""
    assert env._is_fish_shell() is False
    assert env._is_bash_shell() is False
    assert env._is_zsh_shell() is False


def test_create_bundle(tmpdir, monkeypatch):
    # make sure it exists
    runner = CliRunner()

    NAME = "damona__testing__environ__create_bundle"

    if NAME not in Environ().environment_names:
        results = runner.invoke(script.create, [NAME])

    manager = Damona()
    monkeypatch.setenv("DAMONA_ENV", str(manager.damona_path / "envs" / NAME))
    cmd = "damona install fastqc --force"
    status = subprocess.call(cmd.split())

    directory = tmpdir.mkdir("bundle")
    destination = directory / "test"
    # print(destination)
    e = Environment(NAME)
    e.create_bundle()
    os.remove(f"damona_{NAME}.tar")

    # cleanup
    with mock.patch.object(builtins, "input", lambda _: "y"):
        results = runner.invoke(script.delete, [NAME])
