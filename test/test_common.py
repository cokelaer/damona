from damona.common import *

import os
import pytest

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


def test_path():
    # os.environ['DAMONA_PATH'] = '/tmp'
    d = Damona()
    d.config_path

    d.find_orphan_binaries()
    d.get_environments()
    d.find_orphan_images()


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



