
import builtins


from damona.install import LocalImageInstaller

from click.testing import CliRunner
from damona import Environ
from damona import script
from damona import Damona
import mock

from . import test_dir


def test_local_image_installer():

    pass
    # define a dummy environ
    #lii = LocalImageInstaller(test_dir + "/data/testing_1.0.0.img")


def test_cmd():
    from damona.install import CMD
    c = CMD(["damona", "install"])
    c.__repr__()



def test_ImageInstaller(monkeypatch):

    runner = CliRunner()
    setup()
    manager = Damona()
    monkeypatch.setenv("DAMONA_ENV", str(manager.damona_path / "envs/damona__testing__"))

    # This re-installs the image, interfering with the user's local image but should be safe
    results = runner.invoke(script.install, [f"{test_dir}/data/testing_1.0.0.img", "--binaries", "hello", "--force"])
    assert results.exit_code == 0

    # This will fail because hello2 is not in the image
    results = runner.invoke(script.install, [f"{test_dir}/data/testing_1.0.0.img", "--binaries", "hello2", "--force"])
    assert results.exit_code == 1

    # Fails because file does not exist
    results = runner.invoke(script.install, [f"{test_dir}/data/testing_2.0.0.img", "--binaries", "hello2", "--force"])
    assert results.exit_code == 1

    # and not a directory
    results = runner.invoke(script.install, [f"{test_dir}/data", "--binaries", "hello2", "--force"])
    assert results.exit_code == 1


    teardown()


def teardown():
    runner = CliRunner()
    with mock.patch.object(builtins, "input", lambda _: "y"):
        results = runner.invoke(script.env, ["--delete", "damona__testing__"])
        assert results.exit_code == 0



def setup():
    runner = CliRunner()
    if "damona__testing__" not in Environ().environment_names:
        results = runner.invoke(script.env, ["--create", "damona__testing__"])
        assert results.exit_code == 0


