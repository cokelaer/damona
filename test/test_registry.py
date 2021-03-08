from damona.registry import Software, Registry
import glob




def test_single_registry():


    from damona.recipes import __path__
    _registry_files = glob.glob(__path__[0] + '/*/registry.yaml')


    # binaries is not provided and found from the registry name
    salmon_registry = [x for x in _registry_files if "salmon" in x][0]
    sr = Software(salmon_registry)
    assert sr.releases['1.3.0'].binaries == ['salmon']


    # binaries is provided explicitly in the general section
    fastqc_registry = [x for x in _registry_files if "/fastqc/" in x][0]
    sr = Software(fastqc_registry)
    assert sr.releases['0.11.9'].binaries == ['fastqc']

    # binaries are provided explicitly in the releases section. Here there are
    # two releases with different binary names
    kraken_registry = [x for x in _registry_files if "kraken" in x][0]
    sr = Software(kraken_registry)
    assert sr.releases['1.1'].binaries == ['kraken']
    assert sr.releases['2.0.9'].binaries == ['kraken2', 'kraken2-build']

    sr.check()
    sr.binaries
    sr.md5
    sr.releases
    sr.versions
   


def test_registry():

    reg = Registry() 
    reg.get_list()



