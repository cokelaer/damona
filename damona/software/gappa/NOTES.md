gappa is built from source (no micromamba): a multi-stage recipe compiles a static, stripped
binary on `debian:bookworm-slim`, then copies only that binary onto `alpine:3.22` plus `bash`
(needed by Snakemake and Nextflow wrappers). The images are about 7 MB, against about 50 MB for the
former micromamba build of 0.8.0. Outputs of the source-built 0.8.0 were byte-identical to that
micromamba build across ten subcommands (this comparison does not apply to 0.8.0 against 0.9.0).

Pinned: the gappa git tag with its commit and the genesis submodule commit (both asserted in the
recipe), the Debian build packages, and `bash` on Alpine. CLI11 and sparsepp are fixed by the tag's
submodule links and are not asserted.

Not pinned:

- Base images are pinned by tag only (`debian:bookworm-slim`, `alpine:3.22`), not by digest.
- The dependencies of Alpine's `bash` (readline, ncurses, musl, busybox) resolve to whatever the 3.22
  repository holds at build time. The gappa binary itself is fixed by commit and asserted in `%test`,
  but the image is not bit-for-bit reproducible.
- The pinned apt and apk versions only resolve while the repositories still serve them, so an old
  recipe may eventually fail to build rather than drift silently.

Build notes:

- The binary is a static glibc executable that runs on Alpine (musl).
- 0.9.0 needs a link-line workaround: the recipe removes the trailing `-Wl,-Bdynamic` from cmake's
  generated `link.txt`, which otherwise makes the LTO static link fail. The `sed` does not fail when
  the pattern is absent, and `%test` does not check that the binary is static.
- The linker prints a harmless `dlopen` warning from libgomp (OpenMP offload probing). It is never
  triggered at runtime and gappa does no NSS or DNS lookups.

Differences between 0.8.0 and 0.9.0:

- `prepare extract` became `edit extract`, and `prepare clean-tree` is new. The default basal output
  file is now `basal.jplace` (was `basal_branches.jplace`).
- `heat-tree` SVG canvas size and edgepca `transformation.csv` layout differ, and edgepca writes
  extra eigenvalue and eigenvector files. Other tested outputs were identical.

Runtime notes:

- `edit merge` writes pqueries in a different order on every run and `simulate` is random by design.
- gappa's default `--threads` is 10. Cap it explicitly, for example `--threads 4`.
