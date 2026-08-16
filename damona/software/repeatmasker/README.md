# repeatmasker

**DOI:** [10.5281/zenodo.13391622](https://doi.org/10.5281/zenodo.13391622)

## Binaries

`RepeatMasker` `segmasker` `rmblastn` `rmOutToGFF3.pl` `ProcessRepeats` `RM2Bed.py` `RepeatProteinMask`

## Installation

```bash
damona install repeatmasker               # latest (4.2.4)
damona install repeatmasker:VERSION        # specific version
```

## Available Versions

| Version | Size | Binaries | DOI |
|---------|------|----------|-----|
| **4.2.4** *(latest)* | 289.84 MB | `ProcessRepeats` `RM2Bed.py` `RepeatMasker` `RepeatProteinMask` `rmOutToGFF3.pl` `rmblastn` `segmasker` | [10.5281/zenodo.21894048](https://doi.org/10.5281/zenodo.21894048) |

## Notes

**The 4.2.2 image also contains RepeatMasker 4.2.4.** Its recipe pinned no
version, so bioconda resolved to whatever was current at build time. Comparing
4.2.2 with 4.2.4 therefore compares packaging, not the software. 4.2.4 pins the
version explicitly.

**4.2.4 is 43% smaller than 4.2.2** (290 MB against 511 MB) with the same Dfam
4.0 curated consensus coverage. Most of the difference is debug symbols:
conda-forge and bioconda ship `.so` files carrying a full `.debug_info` section.

**`DupMasker` is not exposed as a binary.** It needs
`Libraries/dupliconlib.fa`, which bioconda does not package and
repeatmasker.org no longer distributes, so it has never been able to run in
these images. The script is still present; bind-mount your own copy of the
library over `/opt/conda/envs/main/share/RepeatMasker/Libraries/` to use it.

**`RepeatProteinMask` needs no `--writable-tmpfs` in 4.2.4.** The
`PROT-Dfam_*` protein library it would otherwise generate on first run — which
fails on a read-only container — is baked into the image. In 4.2.2 this
command fails outright, since that recipe deletes the `blastx` it calls.

**Search engines.** RMBlast is the default. `-engine hmmer` additionally needs
the `dfam40.curated.hmm.0.h5` partition, which is not shipped in order to keep
the image small.
