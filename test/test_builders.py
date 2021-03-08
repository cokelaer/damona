import os

from damona.builders import BuilderFromDocker


import pytest
skiptravis = pytest.mark.skipif("TRAVIS_PYTHON_VERSION" in os.environ, reason="On travis. no sudo")

@skiptravis
def test_docker():

    import tempfile
    with tempfile.TemporaryDirectory() as td:
        bb = BuilderFromDocker()
        bb.build("docker://biocontainers/hisat2:v2.1.0-2-deb_cv1", 
            destination=td + "/test.img")
