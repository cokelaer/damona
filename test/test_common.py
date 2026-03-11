import os
import pathlib

import pytest

from damona.common import *

from . import test_dir


def test_no_path(monkeypatch):

    monkeypatch.delenv("DAMONA_PATH", raising=False)
    try:
        DamonaInit()
        assert False
    except:
        assert True
    try:
        Damona()
        assert False
    except:
        assert True


def test_get_shell_config_status_all_unconfigured(tmp_path, monkeypatch):
    """_get_shell_config_status returns configured=False when RC files are absent."""
    # Point home to a temporary directory so no real RC files are found
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setattr(pathlib.Path, "home", staticmethod(lambda: tmp_path))

    init = object.__new__(DamonaInit)
    status = init._get_shell_config_status()

    assert set(status.keys()) == {"bash", "zsh", "fish"}
    for shell, info in status.items():
        assert info["configured"] is False, f"Expected {shell} to be unconfigured"


def test_get_shell_config_status_configured(tmp_path, monkeypatch):
    """_get_shell_config_status returns configured=True when the source line is present."""
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setattr(pathlib.Path, "home", staticmethod(lambda: tmp_path))

    # Write a .bashrc containing the expected source line
    bashrc = tmp_path / ".bashrc"
    bashrc.write_text("source ~/.config/damona/damona.sh\n")

    init = object.__new__(DamonaInit)
    status = init._get_shell_config_status()

    assert status["bash"]["configured"] is True
    assert status["zsh"]["configured"] is False
    assert status["fish"]["configured"] is False


def test_report_missing_config_no_rc_files(tmp_path, monkeypatch, caplog):
    """_report_missing_config warns about missing config when no RC files exist."""
    import logging

    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setattr(pathlib.Path, "home", staticmethod(lambda: tmp_path))

    init = object.__new__(DamonaInit)
    with caplog.at_level(logging.CRITICAL, logger="damona.common"):
        init._report_missing_config()

    combined = caplog.text
    assert "DAMONA_PATH" in combined
    # Should show the echo commands for all three shells
    assert 'echo "source ~/.config/damona/damona.sh" >> ~/.bashrc' in combined
    assert 'echo "source ~/.config/damona/damona.zsh" >> ~/.zshrc' in combined
    assert 'echo "source ~/.config/damona/damona.fish" >> ~/.config/fish/config.fish' in combined
    # When no shells are configured, message should say "To configure damona, run:"
    assert "To configure damona, run:" in combined


def test_report_missing_config_with_configured_shell(tmp_path, monkeypatch, caplog):
    """_report_missing_config tells user to source their file when RC is already configured."""
    import logging

    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setattr(pathlib.Path, "home", staticmethod(lambda: tmp_path))

    # Pre-configure bash
    bashrc = tmp_path / ".bashrc"
    bashrc.write_text("source ~/.config/damona/damona.sh\n")

    init = object.__new__(DamonaInit)
    with caplog.at_level(logging.CRITICAL, logger="damona.common"):
        init._report_missing_config()

    combined = caplog.text
    assert "DAMONA_PATH" in combined
    # Should mention that bash is already configured and instruct to source the file
    assert "bash" in combined
    assert str(bashrc) in combined
    # Should still show commands for unconfigured shells
    assert 'echo "source ~/.config/damona/damona.zsh" >> ~/.zshrc' in combined
    assert "To configure damona for additional shells, run:" in combined


def test_path():
    # os.environ['DAMONA_PATH'] = '/tmp'
    d = Damona()
    d.config_path

    d.find_orphan_binaries()
    d.get_environments()
    d.find_orphan_images()
    d.is_image_used("fastqc_0.11.9")


def test_ImageReader():

    try:
        ir = ImageReader(f"{test_dir}/data/testing_1.0.0")
        assert False
    except SystemExit:
        assert True

    ir = ImageReader(f"{test_dir}/data/testing_1.0.0.img")
    assert ir.version == "1.0.0"
    ir.md5
    ir.guessed_executable
    ir.is_orphan()
    ir.is_installed()
    print(ir)
