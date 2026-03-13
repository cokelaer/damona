import os
import subprocess
import sys
import tempfile

import pytest

from damona.publisher import Publisher

from . import test_dir


def test_publisher_init():
    recipe = f"{test_dir}/data/Singularity.testing_1.0.0"
    pub = Publisher(recipe, force=False)
    assert pub.recipe == recipe
    assert pub.mode == "sandbox.zenodo"
    assert pub.token is None
    assert pub.force is False
    assert pub.destination == "testing_1.0.0.img"


def test_publisher_init_invalid_recipe():
    with pytest.raises(SystemExit):
        Publisher("/tmp/not_a_singularity_recipe")


def test_publisher_init_custom_destination():
    recipe = f"{test_dir}/data/Singularity.testing_1.0.0"
    pub = Publisher(recipe, destination="/tmp/custom_1.0.0.img", mode="zenodo", force=True)
    assert pub.destination == "/tmp/custom_1.0.0.img"
    assert pub.mode == "zenodo"
    assert pub.force is True


def test_publisher_build(mocker):
    recipe = f"{test_dir}/data/Singularity.testing_1.0.0"
    pub = Publisher(recipe, destination="/tmp/test_pub_1.0.0.img")

    mock_builder = mocker.MagicMock()
    mocker.patch("damona.publisher.BuilderFromSingularityRecipe", return_value=mock_builder)

    pub.build()

    mock_builder.build.assert_called_once_with(recipe, destination="/tmp/test_pub_1.0.0.img", force=False)


def test_publisher_check_pass(mocker):
    recipe = f"{test_dir}/data/Singularity.testing_1.0.0"
    pub = Publisher(recipe, destination="/tmp/test_pub_1.0.0.img")

    # Both python and bash found (returncode 0)
    mock_result = mocker.MagicMock()
    mock_result.returncode = 0
    mocker.patch("subprocess.run", return_value=mock_result)

    result = pub.check()
    assert result is True


def test_publisher_check_no_python(mocker):
    recipe = f"{test_dir}/data/Singularity.testing_1.0.0"
    pub = Publisher(recipe, destination="/tmp/test_pub_1.0.0.img")

    # python not found (returncode 1), bash found (returncode 0)
    mock_python = mocker.MagicMock()
    mock_python.returncode = 1
    mock_bash = mocker.MagicMock()
    mock_bash.returncode = 0
    mocker.patch("subprocess.run", side_effect=[mock_python, mock_bash])

    result = pub.check()
    assert result is True


def test_publisher_check_no_bash(mocker):
    recipe = f"{test_dir}/data/Singularity.testing_1.0.0"
    pub = Publisher(recipe, destination="/tmp/test_pub_1.0.0.img")

    # python found but bash not found
    mock_python = mocker.MagicMock()
    mock_python.returncode = 0
    mock_bash = mocker.MagicMock()
    mock_bash.returncode = 1
    mocker.patch("subprocess.run", side_effect=[mock_python, mock_bash])

    with pytest.raises(SystemExit):
        pub.check()


def test_publisher_upload(mocker):
    recipe = f"{test_dir}/data/Singularity.testing_1.0.0"
    pub = Publisher(recipe, destination="/tmp/test_pub_1.0.0.img", token="dummy_token")

    mock_zenodo = mocker.MagicMock()
    mocker.patch("damona.publisher.Zenodo", return_value=mock_zenodo)

    pub.upload()

    mock_zenodo._upload.assert_called_once_with("/tmp/test_pub_1.0.0.img")


def test_publisher_publish(mocker):
    recipe = f"{test_dir}/data/Singularity.testing_1.0.0"
    pub = Publisher(recipe, destination="/tmp/test_pub_1.0.0.img", token="dummy_token")

    mock_build = mocker.patch.object(pub, "build")
    mock_check = mocker.patch.object(pub, "check")
    mock_upload = mocker.patch.object(pub, "upload")

    pub.publish()

    mock_build.assert_called_once()
    mock_check.assert_called_once()
    mock_upload.assert_called_once()
