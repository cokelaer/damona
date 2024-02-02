from snakemake import shell

image = "canu_2.1.1.img"


def test_canu():
    shell(f"singularity exec {image} canu --help")
