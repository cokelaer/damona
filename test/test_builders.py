import os
import tempfile

from damona.builders import BuilderFromDocker, BuilderFromSingularityRecipe
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
