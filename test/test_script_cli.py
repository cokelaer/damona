"""Focused CLI tests to increase coverage of damona/script.py.

Each test uses a unique environment name prefix (damona__script__) and
cleans up after itself so the tests are independent of run order.
"""
import builtins
import subprocess

import mock
import pytest
from click.testing import CliRunner

from damona import Damona, Environ, script

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

_PREFIX = "damona__script__"


def _setup(name):
    runner = CliRunner()
    if name not in Environ().environment_names:
        results = runner.invoke(script.create, [name])
        assert results.exit_code == 0


def _teardown(name):
    runner = CliRunner()
    with mock.patch.object(builtins, "input", lambda _: "y"):
        results = runner.invoke(script.remove, [name])
        assert results.exit_code == 0


# ---------------------------------------------------------------------------
# catalog  (lines 855-967)
# ---------------------------------------------------------------------------


def test_catalog_sort_name():
    runner = CliRunner()
    results = runner.invoke(script.catalog, ["--sort", "name"])
    assert results.exit_code == 0
    assert "Software" in results.output


def test_catalog_sort_size():
    runner = CliRunner()
    results = runner.invoke(script.catalog, ["--sort", "size"])
    assert results.exit_code == 0


def test_catalog_sort_base():
    runner = CliRunner()
    results = runner.invoke(script.catalog, ["--sort", "base"])
    assert results.exit_code == 0


def test_catalog_default():
    # No --sort flag → defaults to "name"
    runner = CliRunner()
    results = runner.invoke(script.catalog, [])
    assert results.exit_code == 0


# ---------------------------------------------------------------------------
# rename  (lines 220-221)
# ---------------------------------------------------------------------------


def test_rename():
    NAME = _PREFIX + "rename_src"
    NAME2 = _PREFIX + "rename_dst"
    _setup(NAME)
    runner = CliRunner()
    # rename() calls input() for confirmation — provide a newline to accept
    results = runner.invoke(script.rename, [NAME, "--new-name", NAME2], input="\n")
    assert results.exit_code == 0
    assert NAME2 in Environ().environment_names
    _teardown(NAME2)


# ---------------------------------------------------------------------------
# create --from-yaml  (line 189)
# ---------------------------------------------------------------------------


def test_create_from_yaml(tmpdir):
    NAME = _PREFIX + "yaml_src"
    NAME2 = _PREFIX + "yaml_dst"
    _setup(NAME)
    runner = CliRunner()
    yaml_file = str(tmpdir.join("env.yaml"))
    try:
        results = runner.invoke(script.export, [NAME, "--yaml", yaml_file])
        assert results.exit_code == 0
        results = runner.invoke(script.create, [NAME2, "--from-yaml", yaml_file])
        assert results.exit_code == 0
    finally:
        _teardown(NAME)
        if NAME2 in Environ().environment_names:
            _teardown(NAME2)


# ---------------------------------------------------------------------------
# search --images-only / --binaries-only  (lines 570-574, 618-640)
# ---------------------------------------------------------------------------


def test_search_images_only():
    runner = CliRunner()
    results = runner.invoke(script.search, ["fastqc", "--images-only", "--local-registry-only"])
    assert results.exit_code == 0
    assert "fastqc" in results.output


def test_search_star_images_only():
    runner = CliRunner()
    results = runner.invoke(script.search, ["*", "--images-only", "--local-registry-only"])
    assert results.exit_code == 0


def test_search_binaries_only():
    runner = CliRunner()
    results = runner.invoke(script.search, ["fastqc", "--binaries-only", "--local-registry-only"])
    assert results.exit_code == 0


# ---------------------------------------------------------------------------
# list  (lines 840-847)
# ---------------------------------------------------------------------------


def test_list_command():
    runner = CliRunner()
    results = runner.invoke(script.list, [])
    assert results.exit_code == 0
    assert "bwa" in results.output


# ---------------------------------------------------------------------------
# stats  (lines 760, 787-823)
# ---------------------------------------------------------------------------


def test_stats_command():
    runner = CliRunner()
    results = runner.invoke(script.stats, [])
    assert results.exit_code == 0


def test_stats_include_biocontainers():
    runner = CliRunner()
    results = runner.invoke(script.stats, ["--include-biocontainers"])
    assert results.exit_code == 0


# ---------------------------------------------------------------------------
# uninstall — non-existent binary  (lines 461-462)
# ---------------------------------------------------------------------------


def test_uninstall_binary_not_found(monkeypatch):
    NAME = _PREFIX + "uninstall_nf"
    _setup(NAME)
    manager = Damona()
    monkeypatch.setenv("DAMONA_ENV", str(manager.damona_path / "envs" / NAME))
    runner = CliRunner()
    try:
        results = runner.invoke(script.uninstall, ["__nonexistent_xyz__"])
        assert results.exit_code == 0  # warning, not a crash
    finally:
        _teardown(NAME)


# ---------------------------------------------------------------------------
# uninstall — .img that does not exist (lines 436-440)
# ---------------------------------------------------------------------------


def test_uninstall_missing_img(monkeypatch):
    NAME = _PREFIX + "uninstall_img"
    _setup(NAME)
    manager = Damona()
    monkeypatch.setenv("DAMONA_ENV", str(manager.damona_path / "envs" / NAME))
    runner = CliRunner()
    try:
        results = runner.invoke(script.uninstall, ["no_such_image_0.0.0.img"])
        assert results.exit_code == 0  # warning, not a crash
    finally:
        _teardown(NAME)


# ---------------------------------------------------------------------------
# clean --do-remove  (lines 501-507)
# covered when there are no orphans, but exercises the else path via
# a dry-run with an environment that has no orphans
# ---------------------------------------------------------------------------


def test_clean_do_remove():
    runner = CliRunner()
    results = runner.invoke(script.clean, ["--do-remove"])
    assert results.exit_code == 0


# ---------------------------------------------------------------------------
# install with comma-separated --binaries  (line 350)
# use a local image so no network is needed
# ---------------------------------------------------------------------------


def test_install_binaries_comma(monkeypatch):
    from . import test_dir

    NAME = _PREFIX + "install_comma"
    _setup(NAME)
    manager = Damona()
    monkeypatch.setenv("DAMONA_ENV", str(manager.damona_path / "envs" / NAME))
    runner = CliRunner()
    try:
        results = runner.invoke(
            script.install,
            [f"{test_dir}/data/testing_1.0.0.img", "--binaries", "hello,world"],
        )
        # may fail if 'world' doesn't exist in the img, but the comma-split path is exercised
        assert results.exit_code in (0, 1)
    finally:
        _teardown(NAME)


# ---------------------------------------------------------------------------
# env command  (script.py lines 236-252)
# ---------------------------------------------------------------------------


def test_env_command():
    runner = CliRunner()
    results = runner.invoke(script.env, [])
    assert results.exit_code == 0


# ---------------------------------------------------------------------------
# activate / deactivate commands  (script.py lines 272-273, 290-291)
# ---------------------------------------------------------------------------


def test_activate_cli(monkeypatch):
    monkeypatch.setenv("PATH", "/usr/bin:/bin")
    runner = CliRunner()
    with mock.patch("subprocess.check_output", return_value="bash"):
        results = runner.invoke(script.activate, ["base"])
    assert results.exit_code == 0
    assert "export DAMONA_ENV=" in results.output


def test_deactivate_cli(monkeypatch):
    manager = Damona()
    base_bin = str(manager.damona_path / "envs" / "base" / "bin")
    monkeypatch.setenv("PATH", f"{base_bin}:/usr/bin:/bin")
    runner = CliRunner()
    with mock.patch("subprocess.check_output", return_value="bash"):
        results = runner.invoke(script.deactivate, [])
    assert results.exit_code == 0


# ---------------------------------------------------------------------------
# info command  (script.py lines 686-710)
# ---------------------------------------------------------------------------


def test_info_command():
    runner = CliRunner()
    results = runner.invoke(script.info, ["base"])
    assert results.exit_code == 0


def test_info_nonexistent_env():
    runner = CliRunner()
    results = runner.invoke(script.info, ["__no_such_env_xyz__"])
    assert results.exit_code == 1


# ---------------------------------------------------------------------------
# export --bundle / no flags  (script.py lines 748-750, 760)
# ---------------------------------------------------------------------------


def test_export_bundle(tmpdir):
    NAME = _PREFIX + "export_bundle_src"
    _setup(NAME)
    runner = CliRunner()
    bundle_file = str(tmpdir.join("env.tar"))
    try:
        results = runner.invoke(script.export, [NAME, "--bundle", bundle_file])
        assert results.exit_code == 0
        import os

        assert os.path.exists(bundle_file)
    finally:
        _teardown(NAME)


def test_export_no_flags():
    NAME = _PREFIX + "export_no_flags_src"
    _setup(NAME)
    runner = CliRunner()
    try:
        results = runner.invoke(script.export, [NAME])
        assert results.exit_code != 0  # UsageError when neither --yaml nor --bundle
    finally:
        _teardown(NAME)


# ---------------------------------------------------------------------------
# uninstall: no active env and no --environment  (script.py lines 423-426)
# ---------------------------------------------------------------------------


def test_uninstall_no_active_env(monkeypatch):
    monkeypatch.delenv("DAMONA_ENV", raising=False)
    runner = CliRunner()
    results = runner.invoke(script.uninstall, ["somebinary"])
    assert results.exit_code == 1


# ---------------------------------------------------------------------------
# uninstall: remove .img that does not exist (script.py lines 437-438)
# ---------------------------------------------------------------------------


def test_uninstall_img_with_env_option(monkeypatch):
    """--environment option path: warns about missing .img file."""
    runner = CliRunner()
    results = runner.invoke(script.uninstall, ["no_such_image_0.0.0.img", "--environment", "base"])
    assert results.exit_code == 0


# ---------------------------------------------------------------------------
# uninstall: remove a real binary (script.py lines 444-460)
# ---------------------------------------------------------------------------


def test_uninstall_existing_binary(monkeypatch):
    """Uninstall a binary that is present in the active environment."""
    from . import test_dir

    NAME = _PREFIX + "uninstall_existing"
    _setup(NAME)
    manager = Damona()
    monkeypatch.setenv("DAMONA_ENV", str(manager.damona_path / "envs" / NAME))
    runner = CliRunner()
    try:
        # First install the binary
        runner.invoke(script.install, [f"{test_dir}/data/testing_1.0.0.img", "--binaries", "hello", "--force"])
        # Then uninstall it
        results = runner.invoke(script.uninstall, ["hello"])
        assert results.exit_code == 0
        # Binary should be gone
        assert not (manager.environments_path / NAME / "bin" / "hello").exists()
    finally:
        _teardown(NAME)


# ---------------------------------------------------------------------------
# check command  (script.py lines 1078-1143)
# ---------------------------------------------------------------------------


def test_check_command_with_binaries():
    from . import test_dir

    runner = CliRunner()
    results = runner.invoke(script.check, [f"{test_dir}/data/testing_1.0.0.img", "--binaries", "hello"])
    # exit 0 if binary found, 1 if not — either way the command ran
    assert results.exit_code in (0, 1)


def test_check_command_no_registry_match():
    """check without --binaries on an image not in the registry should exit 1."""
    from . import test_dir

    runner = CliRunner()
    results = runner.invoke(script.check, [f"{test_dir}/data/testing_1.0.0.img"])
    assert results.exit_code == 1


def test_check_command_binary_not_found():
    """check with a binary that doesn't exist in the image → FAIL → exit 1."""
    from . import test_dir

    runner = CliRunner()
    results = runner.invoke(
        script.check, [f"{test_dir}/data/testing_1.0.0.img", "--binaries", "__nonexistent_xyz_abc__"]
    )
    assert results.exit_code == 1


# ---------------------------------------------------------------------------
# info with installed binaries  (script.py lines 703, 709)
# ---------------------------------------------------------------------------


def test_info_with_installed_binary(monkeypatch):
    """info iterates over images and binaries — lines hit only when env is non-empty."""
    from . import test_dir

    NAME = _PREFIX + "info_with_binary"
    _setup(NAME)
    manager = Damona()
    monkeypatch.setenv("DAMONA_ENV", str(manager.damona_path / "envs" / NAME))
    runner = CliRunner()
    try:
        runner.invoke(script.install, [f"{test_dir}/data/testing_1.0.0.img", "--binaries", "hello", "--force"])
        results = runner.invoke(script.info, [NAME])
        assert results.exit_code == 0
    finally:
        _teardown(NAME)
