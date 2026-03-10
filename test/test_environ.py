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

    # Primary detection: parent process name via subprocess
    with mock.patch("subprocess.check_output", return_value="fish"):
        assert env._detect_shell() == "fish"
        assert env._is_fish_shell() is True
        assert env._is_bash_shell() is False
        assert env._is_zsh_shell() is False

    with mock.patch("subprocess.check_output", return_value="bash"):
        assert env._detect_shell() == "bash"
        assert env._is_bash_shell() is True

    with mock.patch("subprocess.check_output", return_value="zsh"):
        assert env._detect_shell() == "zsh"
        assert env._is_zsh_shell() is True

    # Login shells may appear as "-zsh" or "-bash"
    with mock.patch("subprocess.check_output", return_value="-zsh"):
        assert env._detect_shell() == "zsh"

    with mock.patch("subprocess.check_output", return_value="-bash"):
        assert env._detect_shell() == "bash"

    # When subprocess fails, fall back to $SHELL
    with mock.patch("subprocess.check_output", side_effect=Exception("ps not found")):
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


def test_fish_activate_deactivate_output(monkeypatch, capsys):
    """Test that fish shell activation/deactivation outputs proper fish commands."""
    import io
    from contextlib import redirect_stdout

    manager = Damona()
    env = Environ()
    monkeypatch.setenv("DAMONA_ENV", str(manager.damona_path / "envs" / "base"))

    with mock.patch("subprocess.check_output", return_value="fish"):
        # --- activate ---
        f = io.StringIO()
        with redirect_stdout(f):
            env.activate("base")
        activate_output = f.getvalue()

        # Must use set -gx (global exported variable), no leading spaces, no semicolons
        assert "set -gx DAMONA_ENV" in activate_output
        assert "set -gx fish_user_paths" in activate_output
        assert "$fish_user_paths" in activate_output
        # No leading spaces (clean output for source/psub)
        for line in activate_output.splitlines():
            assert not line.startswith(" "), f"Unexpected leading space in: {line!r}"

        # --- deactivate with a damona env in PATH and no other damona env ---
        env_bin = str(manager.damona_path / "envs" / "base" / "bin")
        monkeypatch.setenv("PATH", f"{env_bin}:/usr/bin:/bin")

        f2 = io.StringIO()
        with redirect_stdout(f2):
            env.deactivate()
        deactivate_output = f2.getvalue()

        # No more damona envs remaining, so DAMONA_ENV must be unset
        assert "set -e DAMONA_ENV" in deactivate_output
        # Must remove only the specific path from fish_user_paths (targeted removal)
        assert f"string match -v -- '{env_bin}'" in deactivate_output
        # Must NOT use the old destructive approach that wiped all fish_user_paths
        assert "set -e fish_user_paths" not in deactivate_output


def test_create_bundle(tmpdir, monkeypatch):
    # make sure it exists
    runner = CliRunner()

    NAME = "damona__testing__environ__create_bundle"

    if NAME not in Environ().environment_names:
        results = runner.invoke(script.create, [NAME])

    manager = Damona()
    monkeypatch.setenv("DAMONA_ENV", str(manager.damona_path / "envs" / NAME))
    cmd = "damona install bwa --force"
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
