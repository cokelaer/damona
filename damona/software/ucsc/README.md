# ucsc

**DOI:** [10.5281/zenodo.10011489](https://doi.org/10.5281/zenodo.10011489)

## Binaries

`bedGraphToBigWig` `bedCoverage` `bedToBigBed` `bedIntersect`

## Installation

```bash
damona install ucsc               # latest (2.10.0)
damona install ucsc:VERSION        # specific version
```

## Available Versions

| Version | Size | Binaries | DOI |
|---------|------|----------|-----|
| **2.10.0** *(latest)* | 54.99 MB | `bedCoverage` `bedGraphToBigWig` `bedIntersect` `bedToBigBed` | [10.5281/zenodo.21985936](https://doi.org/10.5281/zenodo.21985936) |
| `2.9.0` | 52.26 MB | `bedCoverage` `bedGraphToBigWig` `bedIntersect` `bedToBigBed` | [10.5281/zenodo.21986201](https://doi.org/10.5281/zenodo.21986201) |

## Notes

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
the two odd ones out went unnoticed. The key was both mistyped and misleading.
The deposit is permanent, so the entry is kept but flagged `mislabelled`:
installable by explicit version, hidden from search and from this README.

## How releases are keyed here

**The key is the version the tools print, not the kent release.** It comes from
`bedGraphToBigWig v X.Y` / `bedToBigBed v. X.Y`, so that the registry key agrees
with `--version` output and these containers stop being flagged by version
audits. The kent releases are what the recipes pin, and they remain the only
thing describing the whole image -- **to rebuild, read the pins in the recipe,
never the key.**

| release | kent pins | converters print |
|---------|-----------|------------------|
| 2.9.0   | 445 / 447, rest 377 | v 2.9 / v. 2.9 |
| 2.10.0  | 482 across the board | v 2.10 / v. 2.10 |

## Why 2.9.0 mixes three kent releases on purpose

No single kent release yields v2.9. Measured, not assumed:

```
kent 377  ->  bedGraphToBigWig v 4      bedToBigBed v. 2.7
kent 469  ->  bedGraphToBigWig v 2.10   bedToBigBed v. 2.10
kent 482  ->  bedGraphToBigWig v 2.10   bedToBigBed v. 2.10
```

v2.9 only exists at kent 445/447, and those releases exist *only* for
`ucsc-bedgraphtobigwig` and `ucsc-bedtobigbed`. The other three tools are
published at 332, 357, 366, 377, 469 and 482 only. So the v2.9 generation of the
converters can only be combined with 377 for the rest -- which is precisely the
mix the unpinned build produced. `Singularity.ucsc_2.9.0` pins that mix
explicitly and reproduces the 3.7.7 tool set exactly (same five conda packages,
same build strings), now with a key that matches what the tools report.

## Limits of this scheme

- The banner describes two tools out of five. `bedCoverage`, `bedIntersect` and
  `blastToPsl` print no version at all.
- The banner moves more slowly than the kent release: 2.10 covers kent 469 and
  482 alike. A future kent bump may leave the banner untouched, in which case
  the new release needs a distinguishing suffix (as multiqc does with
  `1.27.0-zenodo1`) rather than a reused key.
