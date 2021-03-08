from damona import script
import damona
import subprocess
import builtins


def test_damona_app():
    from click.testing import CliRunner
    from damona.script import install, build,  env, activate, deactivate
    from damona.script import search
    runner = CliRunner()

    # isntall
    results = runner.invoke(install, ['fastqc:0.11.9'])
    assert results.exit_code == 0

    results = runner.invoke(search, ['fastqc'])
    assert results.exit_code == 0

    
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


def test_help():
    cmd = "damona --help"
    subprocess.call(cmd.split())
    cmd = "damona pull --help"
    subprocess.call(cmd.split())


def test_activate_deactivate():
    cmd = "damona activate base"
    subprocess.call(cmd.split())
    cmd = "damona deactivate"
    subprocess.call(cmd.split())


def test_install_dryrun():
    cmd = "damona install fastqc:0.11.9 --dryrun"
    subprocess.call(cmd.split())

def test_install_wrong():
    # non existing image
    cmd = "damona install tartuffe"  
    try:
        subprocess.call(cmd.split())    
        assert False
    except:
        assert True
