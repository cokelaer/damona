from damona.common import *

import os
import pytest

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
    #os.environ['DAMONA_PATH'] = '/tmp'
    d = Damona()
    d.config_path

    d.find_orphan_binaries()
    d.get_environments()
    d.find_orphan_images()

