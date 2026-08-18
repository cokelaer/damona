**`mafft:7.520.0`'s `%runscript` execs `gffread`, not `mafft`.** The recipe was
copy-pasted from the gffread recipe and the runscript line was never updated,
so `singularity run mafft_7.520.0.img` invokes gffread rather than mafft
(`singularity exec ... mafft` still works, since the binary itself is correct
mafft 7.520). The same recipe also installed `mafft` unpinned.

The deposit is immutable, so 7.520.0 is kept as-is rather than silently
patched. `7.526.0` is a fresh release built from a corrected recipe --
`mafft="7.526"` pinned, single joint `micromamba install`, and a runscript
that actually execs `mafft` -- and should be used in place of 7.520.0 wherever
the default `%runscript` entrypoint matters.
