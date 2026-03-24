import builtins
import io
import os
import pathlib
import shutil
import subprocess
from contextlib import redirect_stdout

import mock
import pytest
from click.testing import CliRunner

import damona
from damona import Damona, script
from damona.environ import Environ, Environment, Images, YamlEnv

from . import test_dir


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

        # Must use set -gx (global exported variable), no leading spaces
        assert "set -gx DAMONA_ENV" in activate_output
        assert "set -gx PATH" in activate_output
        assert "$PATH" in activate_output
        # No leading spaces (clean output for eval)
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
        # Must remove only the specific path from PATH (targeted removal)
        assert f"string match -v -- '{env_bin}'" in deactivate_output
        assert "$PATH" in deactivate_output
        # Must NOT use fish_user_paths
        assert "fish_user_paths" not in deactivate_output


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
        results = runner.invoke(script.remove, [NAME])


def test_environment_contains():
    """Test the __contains__ method of Environment."""
    e = Environment("base")
    # base env has no binaries installed by default
    assert "nonexistent_binary_xyz" not in e


def test_environment_repr():
    """Test the __repr__ method of Environment."""
    e = Environment("base")
    r = repr(e)
    assert "binaries" in r
    assert "Mb" in r


def test_yaml_env(tmp_path):
    """Test YamlEnv class parses a YAML environment file correctly."""
    yaml_content = (
        "name: testenv\n"
        "\nimages:\n"
        "- fastqc_0.11.9.img\n"
        "\nbinaries:\n"
        "- fastqc from fastqc:0.11.9\n"
        "- samtools from samtools_1.16.img\n"
    )
    yaml_file = tmp_path / "test_env.yaml"
    yaml_file.write_text(yaml_content)

    ye = YamlEnv(str(yaml_file))
    assert ye.name == "testenv"
    assert "fastqc_0.11.9.img" in ye.images
    assert len(ye.binaries) == 2
    assert "fastqc from fastqc:0.11.9" in ye.binaries
    assert "samtools from samtools_1.16.img" in ye.binaries


def test_images():
    """Test the Images class: len, files property, and get_disk_usage."""
    imgs = Images()

    n = len(imgs)
    assert isinstance(n, int)
    assert n >= 0

    # get_disk_usage in Mb (default)
    usage_mb = imgs.get_disk_usage()
    assert isinstance(usage_mb, int)
    assert usage_mb >= 0

    # get_disk_usage in raw bytes
    usage_bytes = imgs.get_disk_usage(frmt="bytes")
    assert isinstance(usage_bytes, int)
    assert usage_bytes >= 0

    # files property should agree with len
    files = list(imgs.files)
    assert len(files) == n


def test_get_current_env(monkeypatch):
    """Test get_current_env() returns a Path when DAMONA_ENV is set."""
    manager = Damona()
    expected = str(manager.damona_path / "envs" / "base")
    monkeypatch.setenv("DAMONA_ENV", expected)

    env_path = Environ.get_current_env()
    assert str(env_path) == expected


def test_get_current_env_name_no_warning(monkeypatch):
    """Test get_current_env_name(warning=False) returns None when no env active."""
    monkeypatch.delenv("DAMONA_ENV", raising=False)
    result = Environ.get_current_env_name(warning=False)
    assert result is None


def test_delete_base():
    """Test that deleting the base environment raises SystemExit."""
    env = Environ()
    with pytest.raises(SystemExit):
        env.delete("base")


def test_delete_nonexistent():
    """Test deleting a non-existent environment logs an error without raising."""
    env = Environ()
    # Should not raise; just logs an error
    env.delete(".does_not_exist_at_all_xyz")


def test_delete_force():
    """Test deleting a non-empty environment with force=True."""
    env_manager = Environ()
    NAME = ".dummy_force_delete_test"
    env_manager.create(NAME)

    manager = Damona()
    # Put a file inside to make the directory non-empty
    bin_file = manager.environments_path / NAME / "bin" / "fakebinary"
    bin_file.write_text("#!/bin/sh\n")

    try:
        env_manager.delete(NAME, force=True)
        assert not (manager.environments_path / NAME).exists()
    finally:
        path = manager.environments_path / NAME
        if path.exists():
            shutil.rmtree(path)


def test_activate_invalid_env():
    """Test that activating a non-existent environment raises SystemExit."""
    env = Environ()
    with pytest.raises(SystemExit):
        env.activate("env_that_does_not_exist_xyz_abc")


def test_activate_already_in_path(monkeypatch):
    """Test that activating an env already in PATH is a silent no-op."""
    manager = Damona()
    env_bin = str(manager.damona_path / "envs" / "base" / "bin")
    monkeypatch.setenv("PATH", f"{env_bin}:/usr/bin:/bin")

    env = Environ()
    # Should return without printing or raising
    env.activate("base")


def test_activate_zsh_output(monkeypatch):
    """Test that zsh activation prints correct export commands."""
    manager = Damona()
    monkeypatch.setenv("PATH", "/usr/bin:/bin")

    env = Environ()
    with mock.patch("subprocess.check_output", return_value="zsh"):
        f = io.StringIO()
        with redirect_stdout(f):
            env.activate("base")
        output = f.getvalue()

    assert "export DAMONA_ENV=" in output
    assert "export PATH=" in output


def test_activate_bash_output(monkeypatch):
    """Test that bash activation prints correct export commands."""
    manager = Damona()
    monkeypatch.setenv("PATH", "/usr/bin:/bin")

    env = Environ()
    with mock.patch("subprocess.check_output", return_value="bash"):
        f = io.StringIO()
        with redirect_stdout(f):
            env.activate("base")
        output = f.getvalue()

    assert "export DAMONA_ENV=" in output
    assert "export PATH=" in output


def test_activate_unknown_shell(monkeypatch):
    """Test that activating with an unrecognized shell raises SystemExit."""
    manager = Damona()
    monkeypatch.setenv("PATH", "/usr/bin:/bin")

    env = Environ()
    with mock.patch("subprocess.check_output", side_effect=Exception("ps not found")):
        monkeypatch.setenv("SHELL", "/bin/sh")
        with pytest.raises(SystemExit):
            env.activate("base")


def test_deactivate_with_env_name(monkeypatch):
    """Test deactivation when a specific env name is provided."""
    manager = Damona()
    env_bin = str(manager.damona_path / "envs" / "base" / "bin")
    monkeypatch.setenv("PATH", f"{env_bin}:/usr/bin:/bin")
    monkeypatch.setenv("DAMONA_ENV", str(manager.damona_path / "envs" / "base"))

    env = Environ()
    with mock.patch("subprocess.check_output", return_value="bash"):
        f = io.StringIO()
        with redirect_stdout(f):
            env.deactivate(env_name="base")
        output = f.getvalue()

    # Base was the only damona env, so DAMONA_ENV must be unset
    assert "unset DAMONA_ENV" in output


def test_deactivate_remaining_damona_paths(monkeypatch):
    """Test deactivation when another damona env remains in PATH."""
    manager = Damona()
    base_bin = str(manager.damona_path / "envs" / "base" / "bin")
    # Simulate a second damona env path coming *after* base
    other_bin = str(manager.damona_path / "envs" / "other_env" / "bin")
    monkeypatch.setenv("PATH", f"{base_bin}:{other_bin}:/usr/bin")

    env = Environ()
    with mock.patch("subprocess.check_output", return_value="bash"):
        f = io.StringIO()
        with redirect_stdout(f):
            # Deactivate without name removes the first found damona env (base_bin)
            env.deactivate()
        output = f.getvalue()

    # other_bin still present, so DAMONA_ENV is updated to other_env's parent
    assert "export DAMONA_ENV=" in output


def test_create_existing_env():
    """Test that creating an environment that already exists raises SystemExit."""
    NAME = ".dummy_create_exists_test"
    env_manager = Environ()
    env_manager.create(NAME)
    try:
        with pytest.raises(SystemExit):
            env_manager.create(NAME)
    finally:
        manager = Damona()
        path = manager.environments_path / NAME
        if path.exists():
            shutil.rmtree(path)


def test_copy_not_implemented():
    """Test that Environ.copy() raises NotImplementedError."""
    env = Environ()
    with pytest.raises(NotImplementedError):
        env.copy()


def test_environment_rename():
    """Test successful environment rename with force=True."""
    env_manager = Environ()
    orig_name = ".rename_test_orig"
    new_name = ".rename_test_new"

    env_manager.create(orig_name)
    manager = Damona()

    try:
        e = Environment(orig_name)
        e.rename(new_name, force=True)

        assert e.name == new_name
        assert (manager.environments_path / new_name).exists()
        assert not (manager.environments_path / orig_name).exists()
    finally:
        for name in [orig_name, new_name]:
            path = manager.environments_path / name
            if path.exists():
                shutil.rmtree(path)


def test_create_yaml(tmp_path):
    """Test creating a YAML export of the base environment."""
    e = Environment("base")
    yaml_file = str(tmp_path / "test_export.yaml")
    e.create_yaml(output_name=yaml_file)

    assert pathlib.Path(yaml_file).exists()

    # Verify it can be round-tripped through YamlEnv
    ye = YamlEnv(yaml_file)
    assert ye.name == "base"


def test_create_yaml_default_name(tmp_path, monkeypatch):
    """Test create_yaml() uses 'damona_<name>.yaml' as the default filename."""
    monkeypatch.chdir(tmp_path)
    e = Environment("base")
    e.create_yaml()  # no output_name → defaults to damona_base.yaml

    default_file = tmp_path / "damona_base.yaml"
    assert default_file.exists()


def test_get_current_env_name_warning(monkeypatch):
    """Test get_current_env_name(warning=True) logs a warning and returns None."""
    monkeypatch.delenv("DAMONA_ENV", raising=False)
    # Should not raise, just log a warning and return None
    result = Environ.get_current_env_name(warning=True)
    assert result is None


def test_rename_with_input_prompt(monkeypatch):
    """Test rename() without force=True triggers an input prompt."""
    env_manager = Environ()
    orig_name = ".rename_input_test_orig"
    new_name = ".rename_input_test_new"

    env_manager.create(orig_name)
    manager = Damona()

    try:
        e = Environment(orig_name)
        # Mock input() to simulate the user pressing Enter
        with mock.patch.object(builtins, "input", lambda _: ""):
            e.rename(new_name, force=False)

        assert e.name == new_name
        assert (manager.environments_path / new_name).exists()
    finally:
        for name in [orig_name, new_name]:
            path = manager.environments_path / name
            if path.exists():
                shutil.rmtree(path)


def test_deactivate_remaining_paths_fish(monkeypatch):
    """Test deactivation with remaining damona paths outputs fish syntax."""
    manager = Damona()
    base_bin = str(manager.damona_path / "envs" / "base" / "bin")
    other_bin = str(manager.damona_path / "envs" / "other_env" / "bin")
    monkeypatch.setenv("PATH", f"{base_bin}:{other_bin}:/usr/bin")

    env = Environ()
    with mock.patch("subprocess.check_output", return_value="fish"):
        f = io.StringIO()
        with redirect_stdout(f):
            env.deactivate()
        output = f.getvalue()

    # Fish syntax: set -gx DAMONA_ENV when a damona path remains
    assert "set -gx DAMONA_ENV" in output


# ---------------------------------------------------------------------------
# create_from_yaml coverage  (environ.py lines 629-668)
# ---------------------------------------------------------------------------


def test_create_from_yaml_existing_no_force():
    """create_from_yaml with an existing env and force=False should sys.exit."""
    env_manager = Environ()
    NAME = ".dummy_yaml_existing_no_force"
    env_manager.create(NAME)
    manager = Damona()
    try:
        with pytest.raises(SystemExit):
            env_manager.create_from_yaml(NAME, yaml="dummy.yaml", force=False)
    finally:
        path = manager.environments_path / NAME
        if path.exists():
            shutil.rmtree(path)


def test_create_from_yaml_with_mocked_installers(tmp_path):
    """create_from_yaml exercises image/binary install loops with mocks."""
    yaml_content = "name: testenv\n\nimages:\n- fastqc_0.11.9.img\n\nbinaries:\n- fastqc from fastqc:0.11.9\n"
    yaml_file = tmp_path / "env.yaml"
    yaml_file.write_text(yaml_content)

    NAME = ".dummy_yaml_install_mocked"
    env_manager = Environ()
    manager = Damona()
    try:
        with mock.patch("damona.install.RemoteImageInstaller") as mock_rii_cls, mock.patch(
            "damona.install.BinaryInstaller"
        ) as mock_bi_cls:
            mock_rii_inst = mock.MagicMock()
            mock_rii_cls.return_value = mock_rii_inst
            mock_bi_inst = mock.MagicMock()
            mock_bi_cls.return_value = mock_bi_inst
            env_manager.create_from_yaml(NAME, yaml=str(yaml_file))

        mock_rii_inst.pull_image.assert_called_once_with(force=True)
        mock_bi_inst.install_binaries.assert_called_once()
    finally:
        path = manager.environments_path / NAME
        if path.exists():
            shutil.rmtree(path)


def test_create_from_yaml_existing_force(tmp_path):
    """create_from_yaml with existing env and force=True overwrites (lines 634-635)."""
    yaml_content = "name: testenv\n\nimages:\n\nbinaries:\n"
    yaml_file = tmp_path / "env.yaml"
    yaml_file.write_text(yaml_content)

    NAME = ".dummy_yaml_force_overwrite"
    env_manager = Environ()
    manager = Damona()
    env_manager.create(NAME)
    try:
        with mock.patch("damona.install.RemoteImageInstaller"), mock.patch("damona.install.BinaryInstaller"):
            env_manager.create_from_yaml(NAME, yaml=str(yaml_file), force=True)
        assert (manager.environments_path / NAME).exists()
    finally:
        path = manager.environments_path / NAME
        if path.exists():
            shutil.rmtree(path)


# ---------------------------------------------------------------------------
# create_from_bundle coverage  (environ.py lines 670-735)
# ---------------------------------------------------------------------------


def test_create_from_bundle_existing_no_force():
    """create_from_bundle with existing env and force=False should sys.exit."""
    env_manager = Environ()
    NAME = ".dummy_bundle_existing"
    env_manager.create(NAME)
    manager = Damona()
    try:
        with pytest.raises(SystemExit):
            env_manager.create_from_bundle(NAME, bundle="dummy.tar", force=False)
    finally:
        path = manager.environments_path / NAME
        if path.exists():
            shutil.rmtree(path)


def test_get_current_state_with_binary(tmp_path, monkeypatch):
    """get_current_state and create_yaml populate image/binary entries when env is non-empty."""
    from damona.install import BinaryInstaller

    NAME = ".dummy_state_with_binary"
    env_manager = Environ()
    manager = Damona()
    env_manager.create(NAME)
    monkeypatch.setenv("DAMONA_ENV", str(manager.damona_path / "envs" / NAME))

    try:
        bi = BinaryInstaller(["hello"], f"{test_dir}/data/testing_1.0.0.img")
        bi.install_binaries(force=True)

        e = Environment(NAME)
        state = e.get_current_state()
        assert "binaries" in state
        assert "images" in state
        assert "hello" in state["binaries"]

        # create_yaml lines 214, 223-224 (loop over images/binaries)
        yaml_out = str(tmp_path / "state_env.yaml")
        e.create_yaml(output_name=yaml_out)
        content = pathlib.Path(yaml_out).read_text()
        assert "hello" in content
    finally:
        path = manager.environments_path / NAME
        if path.exists():
            shutil.rmtree(path)


def test_create_from_bundle_bin_only(tmp_path):
    """create_from_bundle with a tar containing only bin/ entries."""
    import tarfile as _tarfile

    NAME = ".dummy_bundle_bin_only"
    env_manager = Environ()
    manager = Damona()

    tar_path = tmp_path / "test_bundle.tar"
    fake_binary = tmp_path / "fakebinary"
    fake_binary.write_text("#!/bin/sh\necho hello\n")

    with _tarfile.open(str(tar_path), "w") as tar:
        tar.add(str(fake_binary), arcname="bin/fakebinary")

    try:
        # rm_tree at the end of create_from_bundle calls .glob() and .rmdir() on
        # the images/ sub-dir; create it up-front so the cleanup succeeds even
        # when no images/ entry exists in the tar.
        with mock.patch("damona.environ.Environ.create") as mock_create:

            def _create_with_images(env_name, force=False):
                env_path = manager.environments_path / env_name
                env_path.mkdir(exist_ok=True)
                (env_path / "bin").mkdir(exist_ok=True)
                (env_path / "images").mkdir(exist_ok=True)

            mock_create.side_effect = _create_with_images
            env_manager.create_from_bundle(NAME, bundle=str(tar_path))

        assert (manager.environments_path / NAME / "bin" / "fakebinary").exists()
    finally:
        path = manager.environments_path / NAME
        if path.exists():
            shutil.rmtree(path)
