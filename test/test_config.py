from damona import script
import damona
import subprocess
import builtins



def test_config():
    from damona.config import Config
    c = Config()
    c.read()


