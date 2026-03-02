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


def test_get_commands():
    get_damona_commands()
