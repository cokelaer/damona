**`kraken --version` reports `Kraken version 1.0` in the 1.1.0 image, but the
image really does contain kraken 1.1.** The version string is baked into the
scripts and is wrong at the source; it is not a packaging mistake here.

The recipe pins the package explicitly:

```
conda install kraken==1.1
```

and the package installed in the image is `kraken-1.1-h470a237_2` (see
`/usr/local/anaconda/conda-meta/`). Every script that package ships prints the
same wrong number, hard-coded rather than read from a version file:

```
/usr/local/anaconda/bin/kraken line 255:  print "Kraken version 1.0\n";
```

`kraken-build`, `kraken-filter`, `kraken-report`, `kraken-translate` and
`kraken-mpa-report` all carry the identical literal. A single stale constant
across the whole 1.1 build points at the release, not at conda: the conda
metadata says 1.1 and only the runtime banner disagrees. (The upstream tag was
not re-checked directly — github.com rate-limited the request — so whether the
1.1 tag itself shipped the stale string or the substitution step in
`install_kraken.sh` failed is not established.)

So the registry key 1.1.0 is correct and should not be "fixed" to 1.0. Any audit
comparing a registry version against `--version` output will flag this
container; the conda package metadata and the pinned recipe are the
authoritative record here, not the binary's self-report.

Unrelated to the above: the 2.0.9 release is kraken2, a separate program with
its own binaries (`kraken2`, `kraken2-build`), not a continuation of these
scripts.
