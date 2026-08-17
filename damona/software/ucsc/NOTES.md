**The release keyed 3.7.7 was never a version of anything.** It is the bioconda
package version `377` with dots inserted.

Bioconda versions these tools by the UCSC *kent source tree* release -- a plain
integer (377, 445, 469, 482). The old recipe pinned nothing, so the solver mixed
three kent releases into one image:

```
ucsc-bedcoverage-377        ucsc-bedintersect-377      ucsc-blasttopsl-377
ucsc-bedgraphtobigwig-445   ucsc-bedtobigbed-447
```

Three packages landed on 377, whoever keyed the release read that as 3.7.7, and
the two odd ones out went unnoticed. The key was both mistyped and, because the
build was never coherent, unfixable: no single number describes that image. It
is flagged `mislabelled` and kept only because its Zenodo deposit is permanent.

## How releases are keyed here

**The key is the version the tools print, not the kent release.** `2.10.0` comes
from `bedGraphToBigWig v 2.10` / `bedToBigBed v. 2.10`, so that the registry key
agrees with `--version` output and this container stops being flagged by every
version audit.

The kent release is still what the recipe pins (`=482` for 2.10.0) and is still
the only number covering the whole image. **To rebuild, read the pins in the
recipe, never the key.** Two limits of the chosen scheme, worth remembering
before keying the next release:

- It describes two tools out of five. `bedCoverage`, `bedIntersect` and
  `blastToPsl` print no version at all.
- It moves more slowly than the kent release: `v 2.9` covers both kent 377 and
  kent 445. A future kent bump may leave the banner untouched, in which case the
  new release needs a distinguishing suffix rather than a bare reused key.
