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

Earlier images of this recipe were keyed **5.3.8**, a number that appears
nowhere in BamQC -- not in a tag, not in the sources, not in the output. It was
almost certainly copied from another tool by mistake. Those deposits have been
delisted rather than flagged, because the image itself is fine; only the label
was wrong, and the identical build is now published under the correct key.

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
