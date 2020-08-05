from damona import script
from damona import pull
import subprocess


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



def test_help():
    cmd = "damona --help"
    subprocess.call(cmd.split())
    cmd = "damona pull --help"
    subprocess.call(cmd.split())


def test_list():
    cmd = "damona list --help"
    subprocess.call(cmd.split())

    cmd = "damona list"
    subprocess.call(cmd.split())

def test_develop():
    try:
        cmd = "damona develop"
        subprocess.call(cmd.split())
        assert False
    except:
        assert True

    from damona.recipes import __path__
    cmd = "damona develop --path {}".format(__path__[0] + "/fastq"  )
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
