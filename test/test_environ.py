from damona import script
import damona
import subprocess
import builtins



def test_environ():
    from damona.environ import Environ
    env = Environ()
    env.N
    env.environments
    env.create(".dummy_test")
    import mock
    with mock.patch.object(builtins, 'input', lambda _: 'y'):
        env.delete(".dummy_test")

