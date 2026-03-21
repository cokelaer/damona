import builtins

import mock
import pytest
from click.testing import CliRunner

from damona import Damona, Environ, script
from damona.install import LocalImageInstaller

from . import test_dir


def test_cmd():
    from damona.install import CMD

    c = CMD(["damona", "install"])
    c.__repr__()


def test_output_name_transformation():
    """Test that docker:// and oras:// URLs produce valid output filenames."""
    import re

    valid_pattern = re.compile(r".+_(v|)\d+\.\d+\.\d+(.+|)\.(img|sif)")

    # docker:// with version tag (no 'v' prefix) - GHCR style
    download_name = "docker://ghcr.io/cokelaer/fastqc:0.11.8"
    output_name = download_name.split("/")[-1]
    output_name += ".img"
    output_name = output_name.replace(":", "_")
    assert output_name == "fastqc_0.11.8.img"
    assert valid_pattern.match(output_name)

    # docker:// with version tag with 'v' prefix - biocontainers style
    download_name = "docker://quay.io/biocontainers/bowtie2:v2.4.1_cv1"
    output_name = download_name.split("/")[-1]
    output_name += ".img"
    output_name = output_name.replace(":", "_")
    assert output_name == "bowtie2_v2.4.1_cv1.img"
    assert valid_pattern.match(output_name)

    # oras:// with version tag - GHCR SIF artifact style
    download_name = "oras://ghcr.io/cokelaer/fastqc:0.11.8"
    output_name = download_name.split("/")[-1]
    output_name += ".img"
    output_name = output_name.replace(":", "_")
    assert output_name == "fastqc_0.11.8.img"
    assert valid_pattern.match(output_name)


def test_ImageInstaller(monkeypatch):

    runner = CliRunner()
    NAME = "damona__testing__install_ImageInstaller"
    Setup(NAME)
    manager = Damona()
    monkeypatch.setenv("DAMONA_ENV", str(manager.damona_path / "envs" / NAME))

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

    Teardown(NAME)


def Teardown(NAME):
    runner = CliRunner()
    with mock.patch.object(builtins, "input", lambda _: "y"):
        results = runner.invoke(script.remove, [NAME])
        assert results.exit_code == 0


def Setup(NAME):
    runner = CliRunner()
    if NAME not in Environ().environment_names:

        results = runner.invoke(script.create, [NAME, "--force"])

        assert results.exit_code == 0
