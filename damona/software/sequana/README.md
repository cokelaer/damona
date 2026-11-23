# sequana

**DOI:** [10.5281/zenodo.5799538](https://doi.org/10.5281/zenodo.5799538)

## Binaries

`sequana` `sequana_coverage` `sequana_taxonomy`

## Installation

```bash
damona install sequana               # latest (0.22.0)
damona install sequana:VERSION        # specific version
```

## Available Versions

| Version | Size | Binaries | DOI |
|---------|------|----------|-----|
| **0.22.0** *(latest)* | 974.11 MB | `sequana` `sequana_coverage` `sequana_taxonomy` | [10.5281/zenodo.20467327](https://doi.org/10.5281/zenodo.20467327) |
| `0.21.0` | 974.39 MB | `sequana` `sequana_coverage` `sequana_taxonomy` | [10.5281/zenodo.19298804](https://doi.org/10.5281/zenodo.19298804) |
| `0.18.0` | 1316.40 MB | `sequana` `sequana_coverage` `sequana_taxonomy` | [10.5281/zenodo.16118560](https://doi.org/10.5281/zenodo.16118560) |
| `0.16.5` | 1194.12 MB | `sequana` `sequana_coverage` `sequana_taxonomy` | [10.5281/zenodo.10460105](https://doi.org/10.5281/zenodo.10460105) |
| `0.16.2` | 721.17 MB | `sequana` `sequana_coverage` `sequana_taxonomy` | [10.5281/zenodo.10258126](https://doi.org/10.5281/zenodo.10258126) |
| `0.16.1` | 690.78 MB | `sequana` `sequana_coverage` `sequana_taxonomy` | [10.5281/zenodo.10209929](https://doi.org/10.5281/zenodo.10209929) |
| `0.15.0` | 606.83 MB | `sequana` `sequana_coverage` `sequana_taxonomy` | [10.5281/zenodo.7863732](https://doi.org/10.5281/zenodo.7863732) |
| `0.14.6` | 663.20 MB | `sequana` `sequana_coverage` `sequana_taxonomy` | [10.5281/zenodo.7734816](https://doi.org/10.5281/zenodo.7734816) |
| `0.12.6` | 503.98 MB | `sequana` `sequana_coverage` `sequana_taxonomy` | [10.5281/zenodo.5799539](https://doi.org/10.5281/zenodo.5799539) |

## Notes

### Why 0.26.0 is smaller (551 MB, against about 1 GB for 0.21.0 and 0.22.0, and 1.1 GB for the first 0.26.0 build)

The 0.26.0 image was first built with the earlier recipe at 1.1 GB. Inspecting it showed where
the space went, and the recipe now removes the following:

- **blast (about 580 MB):** `kraken2` depends on `blast` in conda, but only for `kraken2-build`
  database downloads. Neither `sequana` nor `sequana_coverage` runs it. It is removed with
  `micromamba remove --force blast`, which leaves `perl` and the other dependencies in place.
  Build kraken2 databases with the `sequana_tools` image instead.
- **snpEff and the JVM (about 300 MB):** no Sequana pipeline uses snpEff from this image.
  `sequana_variant_calling` runs both snpEff rules (`snpeff_add_locus_in_fasta` and `snpeff`) in the
  `sequana_tools` image, and the other pipelines use `sequana_tools` as well. Use `sequana_tools`
  for snpEff. A user who runs `sequana` directly and needs snpEff to build a snpEff database
  must use that image or a 0.22.0 or earlier `sequana` image.
- **cython:** needed only to build sequana, uninstalled afterwards.
- **Static libraries (`*.a`), headers, locales and man pages**, and **`build-essential` and `make`**,
  which are only needed at build time.

`.pyc` files are kept on purpose. The image is read-only, so without them Python would recompile
every module in memory at each run, which slows startup (pandas, scipy, matplotlib).

### kaleido and plotly are pinned as a pair

`plotly.write_image()` is used by `sequana/enrichment/kegg.py` (KEGG enrichment bar and scatter
plots) and `sequana/modules_report/panther_enrichment.py` (PANTHER enrichment PDFs). Without a
pinned pair, pip resolves `plotly 7.x` with `kaleido 0.2.1`, and `write_image()` then fails with
"Image export requires the Kaleido package, v1.0.0 or greater". The recipe pins `plotly==5.24.1` with
`kaleido==0.2.1`, whose bundled Chromium (about 220 MB) needs no Chrome install. The older
`sequana` images may have the same defect, because they leave plotly and kaleido unpinned. `%test`
now writes a PNG through `write_image()` so that a bad pair fails the build.

### Where the `sequana` image is used

Searching the Sequana pipelines (`variant_calling`, `rnaseq`, `mapper`, `multitax`, `hic`, `nanocap`,
`ripseq` and others) found no config that points to a `sequana_X.Y.Z.img`. Every `sequana_*`
container entry (`sequana_tools`, `sequana_coverage`, `sequana`) points to a `sequana_tools_*.img`.
The only `sequana_X.Y.Z.img` references are an old `sequana_ripseq` test output (0.16.5) and a
download example in the Sequana installation documentation (0.16.2). This image is meant for
running the `sequana` command line (`sequana_coverage`, `sequana_taxonomy`) directly.

### Not pinned

- `cython` is installed unpinned, but it is uninstalled before the image is finalised.
- The base image is the local `micromamba_2.5.0.img`.
- The Python dependencies of `sequana==0.26.0` other than plotly and kaleido resolve at build time.
- `%test` asserts the sequana, kraken2, samtools and bwa versions, and that `blastn`, `snpEff`
  and `java` are absent.
