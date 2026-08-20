**This image is dustmasker 1.0.0 built from the NCBI BLAST+ 2.17.0 release.**
`dustmasker -version` prints both numbers, the application version first and
the package version second:

```
$ dustmasker -version
dustmasker: 1.0.0
 Package: blast 2.17.0, build Jul  1 2025 08:59:18
```

`dustmasker -version-full-json` confirms the same split: `appname dustmasker`,
`version_info 1.0.0`, inside `package blast 2.17.0`. The registry key is the
application version, 1.0.0, as the registry convention requires.

dustmasker is not released on its own. It is one of the executables of the NCBI
BLAST+ suite, and the recipe extracts it from the official prebuilt tarball:

```
https://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/2.17.0/ncbi-blast-2.17.0+-x64-linux.tar.gz
md5 bdec166721de3b55f90a3badc83538e8   (upstream .md5 file)
```

Only `ncbi-blast-2.17.0+/bin/dustmasker` is kept out of that 282 MB archive
(md5 `7afb509c5ef7768449fc1822e22b8881`); both md5 sums are verified inside
`%post`, and `%test` asserts both version lines, so a drifting upstream artifact
fails the build instead of producing a mislabelled deposit.

**The 1.0.0 registry entry was rewritten to point at this image.** The previous
1.0.0 deposit (Zenodo record 5801365) is `kraken_2.0.9.img`, a 690 MB kraken
image that happens to also ship dustmasker 1.0.0. It is not mislabelled — the
dustmasker inside it really is 1.0.0 — but it carries an entire kraken
installation for a single 21 MB executable. That deposit stays on Zenodo, since
deposits are immutable; the registry now serves this 35 MiB image instead.

Note that the application version is frozen upstream: dustmasker reports 1.0.0
in BLAST+ 2.9, 2.12 and 2.17 alike. The key therefore cannot distinguish one
BLAST+ vintage from another, and a future rebuild against a newer BLAST+ would
land on the same key. The build actually shipped is identified by the pinned
URL and the md5 sums above, and by the `blast 2.17.0` assertion in `%test`.

The three runtime libraries pulled with `apt-get` (`libgomp1`, `zlib1g`,
`libbz2-1.0`) and the `debian:bookworm-slim` base tag are deliberately left
unpinned, in line with the rest of this registry: Debian offers no per-package
version pinning without snapshot.debian.org, and these are ABI-stable shared
libraries rather than the scientific payload. Reproducibility here rests on the
version-carrying tarball URL and the two md5 sums verified in `%post`, not on
the apt layer.
