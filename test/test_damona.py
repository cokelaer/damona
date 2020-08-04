from damona import script
import subprocess




def test_pull():
    cmd = "damona --help"
    subprocess.call(cmd.split())

    cmd = "damona list --help"
    subprocess.call(cmd.split())

    cmd = "damona pull --help"
    subprocess.call(cmd.split())
    
    cmd = "damona list"
    subprocess.call(cmd.split())

    try:
        cmd = "damona develop"
        subprocess.call(cmd.split())
        assert False
    except:
        assert True

    from damona.recipes import __path__
    cmd = "damona develop --path {}".format(__path__[0] + "/fastq"  )
    subprocess.call(cmd.split())


    cmd = "damona pull fastqc:0.11.9 --dryrun"  
    subprocess.call(cmd.split())
    

    # non existing image
    cmd = "damona pull tartuffe"  
    try:
        subprocess.call(cmd.split())    
        assert False
    except:
        assert True
