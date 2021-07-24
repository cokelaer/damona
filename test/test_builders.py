import os

from damona.builders import BuilderFromDocker


def test_docker():

    import tempfile
    with tempfile.TemporaryDirectory() as td:
        bb = BuilderFromDocker()
        bb.build("docker://biocontainers/hisat2:v2.1.0-2-deb_cv1", 
            destination=td + "/test.img")
