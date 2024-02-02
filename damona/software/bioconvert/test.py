from snakemake import shell


def test_bioconvert():
    shell("singularity exec bioconvert_0.6.3.img bioconvert --help")
