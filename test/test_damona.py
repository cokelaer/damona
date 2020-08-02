from damona import damona
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



 
