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


def test_get_container_cmd_singularity(monkeypatch):
    """get_container_cmd returns 'singularity' when it is present."""
    import damona.common as _common

    monkeypatch.setattr(_common, "cmd_exists", lambda cmd: cmd == "singularity")
    assert get_container_cmd() == "singularity"


def test_get_container_cmd_apptainer_only(monkeypatch):
    """get_container_cmd returns 'apptainer' when only apptainer is present."""
    import damona.common as _common

    monkeypatch.setattr(_common, "cmd_exists", lambda cmd: cmd == "apptainer")
    assert get_container_cmd() == "apptainer"


def test_get_container_cmd_neither(monkeypatch):
    """get_container_cmd returns None when neither command is present."""
    import damona.common as _common

    monkeypatch.setattr(_common, "cmd_exists", lambda cmd: False)
    assert get_container_cmd() is None


def test_binary_reader_apptainer(tmp_path):
    """BinaryReader can parse wrapper scripts that use apptainer."""
    import os

    # Create a fake binary wrapper that uses apptainer instead of singularity
    wrapper = tmp_path / "fastqc"
    wrapper.write_text(
        "#!/bin/sh\napptainer -s exec ${DAMONA_SINGULARITY_OPTIONS} "
        '${DAMONA_PATH}/images/fastqc_0.11.9.img fastqc ${1+"$@"}\n'
    )

    br = BinaryReader(wrapper)
    assert "fastqc_0.11.9.img" in br.image


def test_is_damona_binary(tmp_path):
    """Only wrapper scripts are recognised as Damona binaries."""
    wrapper = tmp_path / "fastqc"
    wrapper.write_text(
        "#!/bin/sh\nsingularity -s exec ${DAMONA_SINGULARITY_OPTIONS} "
        '${DAMONA_PATH}/images/fastqc_0.11.9.img fastqc ${1+"$@"}\n'
    )
    assert is_damona_binary(wrapper) is True

    # a real executable (non UTF-8 content) must not be considered as a binary
    elf = tmp_path / "aria2c"
    elf.write_bytes(b"\x7fELF\x02\x01\x01\x00" + bytes(range(160, 256)))
    assert is_damona_binary(elf) is False

    # a text file that is not a wrapper either
    other = tmp_path / "README"
    other.write_text("some documentation\n")
    assert is_damona_binary(other) is False


def test_binary_reader_not_a_wrapper(tmp_path):
    """BinaryReader raises a clear error rather than IndexError/UnicodeDecodeError."""
    elf = tmp_path / "aria2c"
    elf.write_bytes(b"\x7fELF\x02\x01\x01\x00" + bytes(range(160, 256)))

    with pytest.raises(ValueError):
        BinaryReader(elf)


def test_is_damona_binary_non_utf8_without_nul(tmp_path):
    """Binary content without NUL bytes must not raise a UnicodeDecodeError."""
    weird = tmp_path / "weird"
    weird.write_bytes(b"\xff\xfe\xfa\xfb")
    assert is_damona_binary(weird) is False


def test_image_reader_version_with_v_prefix():
    """Image names such as name_v1.2.3.img are supported."""
    ir = ImageReader("/tmp/testing_v1.0.0.img")
    assert ir.version == "1.0.0"
    assert ir.guessed_executable == "testing"


def test_image_reader_delete_not_orphan(tmp_path, monkeypatch):
    """A non-orphan image is kept on disk."""
    image = tmp_path / "testing_1.0.0.img"
    image.write_text("not a real image")
    ir = ImageReader(image)
    monkeypatch.setattr(ImageReader, "is_orphan", lambda self: False)
    ir.delete()
    assert image.exists()


def test_image_reader_is_installed_false(tmp_path, monkeypatch):
    monkeypatch.setenv("DAMONA_PATH", str(tmp_path))
    ir = ImageReader("/tmp/not_installed_1.0.0.img")
    assert ir.is_installed() is False


def test_binary_reader_without_damona_path(tmp_path, monkeypatch):
    """Without DAMONA_PATH the placeholder is kept and is_image_available exits."""
    wrapper = tmp_path / "fastqc"
    wrapper.write_text(
        "#!/bin/sh\nsingularity -s exec ${DAMONA_SINGULARITY_OPTIONS} "
        '${DAMONA_PATH}/images/fastqc_0.11.9.img fastqc ${1+"$@"}\n'
    )
    monkeypatch.delenv("DAMONA_PATH", raising=False)
    br = BinaryReader(wrapper)
    assert br.image == "${DAMONA_PATH}/images/fastqc_0.11.9.img"

    with pytest.raises(SystemExit):
        br.is_image_available()


def test_binary_reader_image_not_available(tmp_path, monkeypatch):
    wrapper = tmp_path / "fastqc"
    wrapper.write_text(
        "#!/bin/sh\nsingularity -s exec ${DAMONA_SINGULARITY_OPTIONS} "
        '${DAMONA_PATH}/images/does_not_exist_0.0.1.img fastqc ${1+"$@"}\n'
    )
    monkeypatch.setenv("DAMONA_PATH", str(tmp_path))
    br = BinaryReader(wrapper)
    assert br.is_image_available() is False


def test_requires_singularity_without_container(monkeypatch):
    """The decorator short-circuits when no container command is available."""
    import damona.common as _common

    monkeypatch.setattr(_common, "get_container_cmd", lambda: None)

    @_common.requires_singularity
    def func(ref):  # pragma: no cover - must not be called
        raise AssertionError("should not be called")

    assert func(None) is None


def test_image_reader_delete_orphan(tmp_path, monkeypatch):
    """An orphan image is removed from disk."""
    image = tmp_path / "testing_1.0.0.img"
    image.write_text("not a real image")
    ir = ImageReader(image)
    monkeypatch.setattr(ImageReader, "is_orphan", lambda self: True)
    ir.delete()
    assert not image.exists()


def test_binary_reader_accepts_string_path(tmp_path):
    """BinaryReader converts a str filename into a pathlib.Path."""
    wrapper = tmp_path / "fastqc"
    wrapper.write_text(
        "#!/bin/sh\nsingularity -s exec ${DAMONA_SINGULARITY_OPTIONS} "
        '${DAMONA_PATH}/images/fastqc_0.11.9.img fastqc ${1+"$@"}\n'
    )
    br = BinaryReader(str(wrapper))
    assert isinstance(br.filename, pathlib.Path)


def test_image_is_orphan_true(tmp_path, monkeypatch):
    """An image with no binary pointing at it is an orphan."""
    import damona.common as _common

    monkeypatch.setattr(_common.Damona, "get_all_binaries", lambda self: [])
    ir = ImageReader("/tmp/notused_1.0.0.img")
    assert ir.is_orphan() is True


def _make_wrapper(directory, name, image):
    wrapper = directory / name
    wrapper.write_text(
        "#!/bin/sh\nsingularity -s exec ${DAMONA_SINGULARITY_OPTIONS} "
        f'${{DAMONA_PATH}}/images/{image} {name} ${{1+"$@"}}\n'
    )
    return wrapper


def test_image_is_orphan_ignores_other_images(tmp_path, monkeypatch):
    """Binaries pointing at *other* images do not keep an image alive."""
    import damona.common as _common

    other = _make_wrapper(tmp_path, "fastqc", "fastqc_0.11.9.img")
    monkeypatch.setattr(_common.Damona, "get_all_binaries", lambda self: {other})
    ir = ImageReader("/tmp/helloworld_1.0.0.img")
    assert ir.is_orphan() is True


def test_image_is_orphan_false_when_used(tmp_path, monkeypatch):
    """An image referenced by a binary is not an orphan."""
    import damona.common as _common

    used = _make_wrapper(tmp_path, "helloworld", "helloworld_1.0.0.img")
    monkeypatch.setattr(_common.Damona, "get_all_binaries", lambda self: {used})
    ir = ImageReader("/tmp/helloworld_1.0.0.img")
    assert ir.is_orphan() is False
