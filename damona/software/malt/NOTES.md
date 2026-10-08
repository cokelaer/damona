## Build notes

- The recipe is `Singularity.malt_0.6.2`: upstream "0.62" (bioconda) is MALT 0.6.2; the binaries print
  `MALT (version 0.6.2, built 12 Sep 2023)`. The registry key is therefore `0.6.2`.
- Not built from source: https://github.com/husonlab/malt has no 0.6.2 tag (only v0.5.2; master is 0.6.3). Commit
  10e91da ("new release", Sep 2023) carries 0.6.2, but its ant build needs sibling checkouts of `jloda` and
  `megan-ce` (unpinned/untagged for that date), JavaFX, and hard-coded author paths. The official vendor
  install4j installer is used instead, pinned by versioned URL and MD5 3e9b7516c722ca959d92722bea209b04
  (the same artefact bioconda packages). It bundles its own JRE in /opt/malt/jre.
- Only `malt-build` and `malt-run` exist in 0.6.2; there is no `malt-decode`.
- The bundled JRE is full (AWT), so `-Djava.awt.headless=true` and relocated java prefs/user.home (/tmp) are
  appended to /opt/malt/malt-{run,build}.vmoptions (read-only HOME safe; no JAVA_TOOL_OPTIONS, which would print
  a "Picked up" line on stderr).
- Unpinned: build-time-only apt packages (curl, ca-certificates, purged afterwards) and the debian:bookworm-slim
  base digest (tag pinned only).
