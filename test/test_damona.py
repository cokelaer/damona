from damona import script
from damona import pull
import subprocess
import builtins

def test_damona_app():
    from click.testing import CliRunner
    from damona.script import install, build, registry, env, activate, deactivate
    from damona.script import list as _list
    runner = CliRunner()

    # isntall
    results = runner.invoke(install, ['fastqc:0.11.9', '--dryrun'])
    assert results.exit_code == 0

    results = runner.invoke(_list)
    assert results.exit_code == 0

    import damona
    results = runner.invoke(registry, ["--path", damona.__path__[0] + "/recipes/fastqc"])
    assert results.exit_code == 0
    
    import damona
    results = runner.invoke(env, [])
    # wrong
    results = runner.invoke(env, ["--create", ".dummy_test", "--delete", ".dummy_test"])
    # good
    results = runner.invoke(env, ["--create", ".dummy_test"])
    assert results.exit_code == 0
    results = runner.invoke(env, ["--create", ".dummy_test"])
    assert results.exit_code == 0
    results = runner.invoke(activate, [".dummy_test"])
    assert results.exit_code == 0
    results = runner.invoke(deactivate, [])
    assert results.exit_code == 0

    import mock
    with mock.patch.object(builtins, 'input', lambda _: 'y'):
        results = runner.invoke(env, ["--delete", ".dummy_test"])
        assert results.exit_code == 0

def test_environ():
    from damona.environ import Environ
    env = Environ()
    env.N
    env.environments
    env.create(".dummy_test")
    import mock
    with mock.patch.object(builtins, 'input', lambda _: 'y'):
        env.delete(".dummy_test")

def test_config():
    from damona.config import Config
    c = Config()
    c.read()


def test_python_pull():
    p = pull.Pull(dryrun=True)
    p.pull("fastqc:0.11.9")
    p.pull("fastqc") # latest
    try:
        p.pull("fastqc1")
        assert False
    except:
        assert True

def test_python_registry():
    from damona import registry
    r = registry.Registry()
    r.get_list()

    from damona.recipes import __path__
    path = __path__[0] + "/fastqc"
    r.create_registry(path)

    r = registry.Registry("damona")
    r.get_list()


def test_help():
    cmd = "damona --help"
    subprocess.call(cmd.split())
    cmd = "damona pull --help"
    subprocess.call(cmd.split())


def test_list():
    cmd = "damona list --help"
    subprocess.call(cmd.split())

    cmd = "damona list --pattern qc"
    subprocess.call(cmd.split())

def test_registry():
    try:
        cmd = "damona registry"
        subprocess.call(cmd.split())
        assert False
    except:
        assert True

    from damona.recipes import __path__
    cmd = "damona registry --path {}".format(__path__[0] + "/fastq"  )
    subprocess.call(cmd.split())

def test_pull_dryrun():
    cmd = "damona pull fastqc:0.11.9 --dryrun"  
    subprocess.call(cmd.split())

def test_pull_wrong():
    # non existing image
    cmd = "damona pull tartuffe"  
    try:
        subprocess.call(cmd.split())    
        assert False
    except:
        assert True
