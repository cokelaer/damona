# cnvkit

## Binaries

`cnvkit.py` `cnv_annotate.py` `cnv_expression_correlate.py` `cnv_updater.py` `genome_instability_index.py` `guess_baits.py` `reference2targets.py` `skg_convert.py` `samtools`

## Installation

```bash
damona install cnvkit               # latest (0.9.10)
damona install cnvkit:VERSION        # specific version
```

## Available Versions

| Version | Size | Binaries | DOI |
|---------|------|----------|-----|
| **0.9.10** *(latest)* | 597.27 MB | `cnv_annotate.py` `cnv_expression_correlate.py` `cnv_updater.py` `cnvkit.py` `genome_instability_index.py` `guess_baits.py` `reference2targets.py` `samtools` `skg_convert.py` | [10.5281/zenodo.23234870](https://doi.org/10.5281/zenodo.23234870) |

## Notes

## Notes

- CNVkit 0.9.10 is built from the upstream git tag `v0.9.10`; runtime dependencies come from conda-forge/bioconda, pinned.
- `scripts/snpfilter.sh` from the upstream source is **not shipped**. It relies on `samtools mpileup --VCF`, which no longer exists in the pinned samtools 1.17, so the script cannot run in this container.
- `pip` and `git` are installed only as build tools (pinned); `git` is removed at the end of the build.
