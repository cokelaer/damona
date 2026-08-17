**The release keyed 2.35.0 is a typo for 2.3.5.** There has never been an
RNA-SeQC 2.35.0; the dot was simply put in the wrong place when the container
was first published.

The recipe behind that image always installed the right package:

```
conda install RNA-seQC==2.3.5
```

and the image holds `rna-seqc-2.3.5-h76d5d7d_1` (see
`/usr/local/anaconda/conda-meta/`), with `rnaseqc --version` printing
`RNASeQC 2.3.5`. So only the registry key, the `Version` label and the image
filename were ever wrong -- the software inside is correct.

The 2.35.0 entry is kept listed rather than delisted: the deposit is on Zenodo
permanently and `sequana_rnaseq` pins it. A correctly named 2.3.5 container has
been rebuilt from the same package on the current micromamba base and is the
one to use from now on.

**Version ordering caveat:** 2.35.0 sorts *above* 2.3.5, so a plain
`damona install rnaseqc` would pick the mislabelled image as "latest". The
2.35.0 entry therefore carries `broken: true`, which keeps it installable by
explicit version (`damona install rnaseqc:2.35.0`) while hiding it from search
and from automatic latest-version selection.
