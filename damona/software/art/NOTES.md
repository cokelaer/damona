**The bioconda `art` package is versioned by release *date*, not by software
version.** The number looks like a version but reads MM.DD.YY, so it never
matches what `art_illumina` prints.

| conda package | upstream ART release | `art_illumina` reports |
|---------------|----------------------|------------------------|
| `art=3.11.14` | ART-VanillaIceCream **03-11-2014** | Q Version 2.1.8 (Mar 8, 2014) |
| `art=3.19.15` | ART-ChocolateCherryCake **03-19-2015** | Q Version 2.3.7 (Mar 19, 2015) |
| `art=2016.06.05` | ART-MountRainier **2016-06-05** | Q Version 2.5.8 (June 6, 2016) |

The 2.3.7 row settles it: the conda version `3.19.15` and the date the binary
prints about itself, `Mar 19, 2015`, are the same day. Upstream numbers its own
releases 2.1.8 / 2.3.7 / 2.5.8 and names them after desserts and mountains; the
conda recipe used the release date instead.

The registry therefore keys every release on the `art_illumina` version, which
is the real one. An earlier deposit was named `art_3.11.14.img` after the conda
date; it has been delisted and re-deposited as `art_2.1.8.img`
([10.5281/zenodo.21980048](https://doi.org/10.5281/zenodo.21980048)), so the
image name, the recipe name and the registry key now all agree.

Note that `art_454` versions independently of `art_illumina` and reports higher
numbers (2.5.8 / 2.6.0 / 2.6.0 across these three images). Any audit that probes
a version out of this container must use `art_illumina`, not the first binary in
the list.
