# bamqc

## Binaries

`bamqc`

## Installation

```bash
damona install bamqc               # latest (0.1.25)
damona install bamqc:VERSION        # specific version
```

## Available Versions

| Version | Size | Binaries | DOI |
|---------|------|----------|-----|
| **0.1.25** *(latest)* | 265.57 MB | `bamqc` | [10.5281/zenodo.21990899](https://doi.org/10.5281/zenodo.21990899) |

## Notes

BamQC is unusual in that it has no version to ask for: upstream publishes no
tags and no GitHub releases, and `master` has been the same commit
(`4b3d20f17b36`) since 2018-02-06.

## Version key

The only version BamQC states about itself is a string hard-coded in its
sources, which the binary prints as:

```
$ singularity exec bamqc_0.1.25.img bamqc --version
BamQC v0.1.25_devel
```

That is where the `0.1.25` key comes from, and `%test` asserts it so the key
cannot drift away from the binary on a future rebuild.

## Reproducibility

With no tag to pin, the recipe pins the commit explicitly. The previous recipe
cloned `master` unpinned, so it happened to be reproducible only because
upstream has been dormant for seven years -- the first commit pushed there would
have silently changed what the image contained.

The build patches `build.xml` from Java 1.6 to 1.8 (modern JDKs refuse to target
1.6), and copies `bin/*` into the source root: the `bamqc` launcher looks for
`.class` files there and aborts if it also finds `.java` files, so the sources
are deleted after compilation. The JDK and ant are purged afterwards but the JRE
must stay -- `bamqc` is a shell wrapper around `java`, which `%test` checks.
