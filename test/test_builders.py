import os
import pathlib
import tempfile

import pytest

from damona.builders import (
    BuilderFromDocker,
    BuilderFromSingularityRecipe,
    fetch_base_image,
    get_bootstrap_info,
)

from . import test_dir


# reach too many requests ??
def test_docker_alpine(monkeypatch):

    # explcitily named the output file
    with tempfile.TemporaryDirectory() as td:
        bb = BuilderFromDocker()
        bb.build("alpine", destination=td + "/alpine.img")

        # we start again to test the force option
        bb.build("alpine", destination=td + "/alpine.img", force=True)

        # we start again to test the input set to yes
        monkeypatch.setattr("builtins.input", lambda _: "yes")
        bb.build("alpine", destination=td + "/alpine.img")

        # we start again to test the input set to no
        monkeypatch.setattr("builtins.input", lambda _: "no")
        bb.build("alpine", destination=td + "/alpine.img")

        # we start again to test the input set to unexpected value
        monkeypatch.setattr("builtins.input", lambda _: "dummy")
        try:
            bb.build("alpine", destination=td + "/alpine.img")
            assert False
        except SystemExit:
            assert True

    try:
        with tempfile.TemporaryDirectory() as td:
            bb = BuilderFromDocker()
            bb.build("alpine", destination=td + "/alpine.wrong_extension")
        assert False
    except:
        assert True


def test_singularity_recipe(monkeypatch):
    bb = BuilderFromSingularityRecipe()

    try:
        bb.build(f"{test_dir}/data/dummy")
        assert False
    except SystemExit:
        assert True

    with tempfile.TemporaryDirectory() as td:
        bb.build(f"{test_dir}/data/Singularity.testing_1.0.0", destination=td + "/test.img")

        # we start again to test the force option
        bb.build(f"{test_dir}/data/Singularity.testing_1.0.0", destination=td + "/test.img", force=True)

        # we start again to test the input set to yes
        monkeypatch.setattr("builtins.input", lambda _: "yes")
        bb.build(f"{test_dir}/data/Singularity.testing_1.0.0", destination=td + "/test.img")

        # we start again to test the input set to no
        monkeypatch.setattr("builtins.input", lambda _: "no")
        bb.build(f"{test_dir}/data/Singularity.testing_1.0.0", destination=td + "/test.img")

        # we start again to test the input set to unexpected value
        monkeypatch.setattr("builtins.input", lambda _: "dummy")
        try:
            bb.build(f"{test_dir}/data/Singularity.testing_1.0.0", destination=td + "/test.img")
            assert False
        except SystemExit:
            assert True


def test_get_bootstrap_info(tmp_path):
    recipe = tmp_path / "Singularity.dummy_1.0.0"
    recipe.write_text(
        "BootStrap: localimage\n"
        "From: ../../library/micromamba/micromamba_2.5.0.img\n"
        "\n"
        "%post\n"
        "  From: not_a_header\n"
    )
    assert get_bootstrap_info(recipe) == ("localimage", "../../library/micromamba/micromamba_2.5.0.img")

    # a docker-based recipe is not concerned
    recipe = tmp_path / "Singularity.dummy_2.0.0"
    recipe.write_text("Bootstrap: docker\nFrom: alpine:3.20\n")
    assert get_bootstrap_info(recipe) == ("docker", "alpine:3.20")
    assert fetch_base_image(recipe) is None


def test_fetch_base_image(tmp_path, monkeypatch):
    image = tmp_path / "micromamba_2.5.0.img"
    recipe = tmp_path / "Singularity.dummy_1.0.0"
    recipe.write_text(f"Bootstrap: localimage\nFrom: {image.name}\n")

    downloaded = {}

    def fake_download(url, filename):
        downloaded["url"] = url
        pathlib.Path(filename).write_text("fake image")
        return pathlib.Path(filename)

    from damona.registry import Software

    expected_md5 = Software("micromamba").releases["2.5.0"].md5sum

    monkeypatch.setattr("damona.utils.download_with_progress", fake_download)
    # the fake content has of course the wrong md5, so pretend it is the expected one
    monkeypatch.setattr("easydev.md5", lambda x: expected_md5)

    assert fetch_base_image(recipe) == image.resolve()
    assert image.exists()
    assert "micromamba_2.5.0.img" in downloaded["url"]

    # image now exists; no download should occur
    downloaded.clear()
    assert fetch_base_image(recipe) == image.resolve()
    assert downloaded == {}


def test_fetch_base_image_unknown_version(tmp_path):
    image = tmp_path / "micromamba_0.0.0.img"
    recipe = tmp_path / "Singularity.dummy_1.0.0"
    recipe.write_text(f"Bootstrap: localimage\nFrom: {image.name}\n")

    with pytest.raises(SystemExit):
        fetch_base_image(recipe)


def test_get_temp_file():
    """Builder.get_temp_file returns a temporary .img file in the damona directory."""
    from damona.builders import Builder, manager

    bb = Builder()
    fh = bb.get_temp_file()
    try:
        assert fh.name.endswith(".img")
        assert os.path.exists(fh.name)
        assert os.path.dirname(fh.name) == str(manager.damona_path)
    finally:
        fh.close()
    # the file is removed when closed
    assert not os.path.exists(fh.name)
