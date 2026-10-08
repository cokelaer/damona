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

## MALT 0.5.2 (built from source)

- Version naming: anaconda/bioconda lists MALT versions as 0.62, 0.61, 0.53 and 0.41. These are not typos; they are
  0.6.2, 0.6.1, 0.5.3 and 0.4.1 with the dots dropped. Damona keys use the dotted version the binaries report
  (`MALT (version 0.5.2, built 28 Jan 2021)`).
- `Singularity.malt_0.5.2` is built from source with plain `javac` (no ant, no module system). `antbuild/build.xml`
  hard-codes sibling checkouts `../../jloda`, `../../megan-ce` and a local JavaFX dir, so the three trees are merged
  into one flat source tree (module-info.java dropped) and MaltBuild/MaltRun are compiled against the repos' `jars/`.
- Pins: husonlab/malt tag v0.5.2 (6f200c7e, 28 Jan 2021); husonlab/jloda a077b9e4 and husonlab/megan-ce 148dedaf, the
  last commits on or before the malt tag date (both 28 Jan 2021 16:03). Neither repo has a tag for that date, hence SHAs.
- JavaFX is needed at runtime even headless (jloda ProgramProperties touches javafx.scene.text.Font), so Debian
  `openjfx` stays in the image (image is about 300 MB vs 150 MB for 0.6.2). `-Dprism.order=sw` and
  `XDG_CACHE_HOME=/tmp` are set in the wrappers to avoid libGL/MESA and fontconfig noise on stderr.
- Unpinned: debian:bookworm-slim digest, apt dependency packages pulled in by the pinned openjdk/openjfx packages,
  build-time git/ca-certificates (purged).
