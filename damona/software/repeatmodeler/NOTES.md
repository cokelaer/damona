## Build notes

- The recipe inherits `docker://dfam/tetools:2.00`. Docker tags are mutable; the
  digest seen at design time (2026-10-13, tag pushed 2026-06-11) was
  `sha256:6081b4d3883eff478873cb94cd24addf540275365d4acc4446bb647a341e95e2`.
  Bootstrap could not use `From: dfam/tetools@sha256:...` together with a readable tag, so the tag is
  pinned and the digest recorded in the recipe comment. `%test` asserts RepeatModeler 2.0.9 and
  RepeatMasker 4.2.4, so a drifting tag fails the build.
- The tetools tag (2.00) is not the RepeatModeler version: the key is the version RepeatModeler reports (2.0.9).
- Nothing inside the image (RMBlast, TRF, RepeatScout, RECON, LTR_retriever, genometools, MAFFT, CD-HIT,
  NINJA) is pinned by this recipe; they are whatever the tetools image contains.
- The Dfam/FamDB partition is NOT in `/opt/RepeatMasker/Libraries/famdb`; `/opt/FamDB-Dfam-4.0/Libraries/famdb`
  holds the (root) data of the image. RepeatModeler itself does not need it, but running
  RepeatMasker with `-species` needs a bind mount or `FAMDB_DIR`/`-libdir`.
- Image size is about 800 MB (not pruned, to stay a minimal inheritance of upstream).
