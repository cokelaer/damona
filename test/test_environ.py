from damona.environ import Environment
from damona.environ import Environ
import damona
import builtins



def test_no_var(monkeypatch):
    monkeypatch.delenv("DAMONA_ENV", raising=False)
    try:
        Environ()
        assert False
    except:
        assert True



def test_environ():
    env = Environ()
    env.N
    env.environments
    env.create(".dummy_test")
    import mock
    with mock.patch.object(builtins, 'input', lambda _: 'y'):
        env.delete(".dummy_test")


    env.get_current_env()
    env.environment_names
    env.activate("base")
    env.deactivate()


def test_environment_no_var(monkeypatch):
    monkeypatch.delenv("DAMONA_PATH", raising=False)
    e = Environment("base")
    try:
        e.get_disk_usage()
        assert False
    except:
        assert True

def test_environment():
    e = Environment("base")
    e.get_installed_binaries()
    #from tempfile import TemporaryFile
    #with TemporaryFile() as fout:
    #    e.create_bundle(output_name=fout.name)

    try:
        e = Environment("base_does_not_exist")
        assert False
    except:
        assert True


