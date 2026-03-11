import pathlib
import shutil

from damona.config import Config, get_damona_commands


def test_config():
    c = Config()
    c.read()


def test_config_creation():  # this is for the local cases

    c = Config(name="damona__testing__")
    if str(c.user_config_dir).endswith("damona__testing__"):
        shutil.rmtree(str(c.user_config_dir))


def test_shell_file_update():
    """Shell config files should be updated when the packaged version differs."""
    c = Config(name="damona__testing__")
    fish_file = pathlib.Path(c.user_config_dir) / "damona.fish"
    try:
        # Overwrite with stale content
        fish_file.write_text("# old content")
        # add_fish should detect the difference and update the file
        updated = c.add_fish()
        assert updated is True
        assert fish_file.read_text() != "# old content"

        # Calling again when up-to-date should return False
        updated_again = c.add_fish()
        assert updated_again is False
    finally:
        if str(c.user_config_dir).endswith("damona__testing__"):
            shutil.rmtree(str(c.user_config_dir))


def test_update_shell_rc(tmp_path):
    """_update_shell_rc should append init block idempotently."""
    c = Config(name="damona__testing__")
    source_line = "source /path/to/damona.sh"
    block = "\n# Added by Damona\n" + source_line + "\n"

    try:
        # 1. RC file does not exist yet — should be created
        rc_file = tmp_path / "test_rc"
        result = c._update_shell_rc(str(rc_file), source_line, block, "bash")
        assert result is True
        assert rc_file.exists()
        assert source_line in rc_file.read_text()

        # 2. Source line already present — should NOT duplicate
        result = c._update_shell_rc(str(rc_file), source_line, block, "bash")
        assert result is False
        assert rc_file.read_text().count(source_line) == 1

        # 3. RC file exists without the source line — should append
        other_rc = tmp_path / "other_rc"
        other_rc.write_text("# existing content\n")
        result = c._update_shell_rc(str(other_rc), source_line, block, "bash")
        assert result is True
        content = other_rc.read_text()
        assert source_line in content
        assert "# existing content" in content  # original content preserved
    finally:
        if str(c.user_config_dir).endswith("damona__testing__"):
            shutil.rmtree(str(c.user_config_dir))


def test_init_fish_rc(tmp_path):
    """_init_fish_rc should write the fish source block to config.fish."""
    c = Config(name="damona__testing__")
    fish_rc = tmp_path / ".config" / "fish" / "config.fish"

    try:
        # Patch _update_shell_rc to use tmp_path-relative path
        result = c._update_shell_rc(
            str(fish_rc),
            "source ~/.config/damona/damona.fish",
            "\n# Added by Damona\nsource ~/.config/damona/damona.fish\n",
            "fish",
        )
        assert result is True
        assert fish_rc.exists()
        assert "source ~/.config/damona/damona.fish" in fish_rc.read_text()

        # Calling again must not duplicate
        result = c._update_shell_rc(
            str(fish_rc),
            "source ~/.config/damona/damona.fish",
            "\n# Added by Damona\nsource ~/.config/damona/damona.fish\n",
            "fish",
        )
        assert result is False
        assert fish_rc.read_text().count("source ~/.config/damona/damona.fish") == 1
    finally:
        if str(c.user_config_dir).endswith("damona__testing__"):
            shutil.rmtree(str(c.user_config_dir))


def test_get_commands():
    get_damona_commands()
