Changelog
=========

Unreleased
----------

**Containers**

- Added recipe: dustmasker 1.0.0, a 35 MiB image extracted from the pinned
  NCBI BLAST+ 2.17.0 tarball. The 1.0.0 entry previously resolved to
  ``kraken_2.0.9.img``, a 690 MB kraken image that happens to ship the same
  dustmasker; installing dustmasker no longer pulls kraken.

**Bug fixes**

- ``damona uninstall`` given an unknown binary name reported only that the
  name was not found in the environment, which reads like the binary was
  never installed. It now appends the closest installed names, so a typo is
  obvious.
- ``damona catalog`` showed ``?`` in the base-image column for 13 releases
  whose Singularity file is not where the registry key says it should be:
  a directory spelled differently (``umi-tools`` lives in ``software/umi_tools``),
  a filename differing in case (``Singularity.qc3C_0.5.0``), a version whose
  suffix uses ``_`` rather than ``-``, or a ``-zenodo1`` re-deposit that shares
  the recipe of its base version. The lookup now falls back to a
  case-insensitive, separator-insensitive search, leaving ``?`` only for the
  four releases that genuinely ship no recipe.

**Mirrors and download resilience**

- A release can now be served by named mirrors as well as by its own Zenodo
  URL. Mirrors are declared in ``damona/software/mirrors.yaml`` as name to
  base URL; the image filename is appended, so adding a mirror does not
  require editing every release. A release whose file is named differently on
  a mirror overrides the full URL under a ``mirrors:`` key in its own
  ``registry.yaml``. The name ``zenodo`` is reserved for the release's own
  ``download`` field.
- ``damona install`` accepts ``--from NAME`` to force a source, ``--no-fallback``
  to stay on the canonical one, and ``--min-speed`` to abandon a slow source.
  With no flag, the canonical source is tried first and mirrors follow, so a
  slow or unavailable Zenodo no longer fails the install. An unknown ``--from``
  name lists the valid ones.
- Transfers now time out, abort when stalled, and can abort when throughput
  stays below a floor; 429 and 503 answers are retried honouring
  ``Retry-After``. If every source is slow, the fastest is used anyway rather
  than failing.
- Downloaded bytes are verified against the registry md5 before the image is
  installed. A source serving different content is discarded and the next one
  is tried, so a mirror never has to be trusted. Previously a mismatch only
  logged a warning after the image had been installed.
- ``damona check-mirrors`` (maintainers) checks that every release resolves on
  every declared mirror, comparing the advertised size with the registry
  filesize, without transferring images. Mirrors declared inside a release
  entry are checked as well as those declared globally, and a release is only
  checked against a mirror it actually resolves to.
- helloworld 1.0.0 and bwa 0.7.17 are mirrored in
  ``sequana/damona-containers`` and serve as the live examples in the test
  suite.

Version 0.23.0 (August 2026)
----------------------------

**Containers**

- Added recipes: repeatmasker 4.2.2 and 4.2.4, seqkit 2.13.0, seqtk 1.5.0,
  barrnap 1.10.6, cufflinks 2.2.1, hicexplorer 3.7.6.
- repeatmasker 4.2.4 is 43% smaller than 4.2.2 (290 MB against 511 MB) for the
  same Dfam 4.0 coverage, mostly by stripping the debug symbols that
  conda-forge and bioconda ship in their shared libraries. It also fixes
  ``RepeatProteinMask``, which no earlier image could run, and pins the
  RepeatMasker version: the image published as 4.2.2 actually contains 4.2.4.
- ``DupMasker`` is no longer advertised for repeatmasker. It requires a
  duplicon library that is not distributed any more, so it never worked.

**Bug fixes**

- ``damona build`` created its temporary image in ``damona.cfg``, a file
  rather than a directory, and failed with ``NotADirectoryError``.
- Listing an environment crashed when its ``bin/`` directory held files
  Damona did not create, such as hand-made symbolic links. Those are now
  detected and skipped.

**Performance**

- ``damona stats`` queried Zenodo once per software, which is slow and hits
  the API rate limit. Lookups are now batched (40 records per request) and
  cached for 24h.

**Documentation**

- Per-software ``README.md`` files are generated; an optional ``NOTES.md``
  next to a recipe is now appended to them, so hand-written caveats survive
  regeneration.
- Reworked the user and developer guides, moved the changelog out of the
  README, and declared support for Python 3.11 and 3.12.

Version 0.22.0 (June 2026)
---------------------------

- Added new recipe: mmseqs2 18.0.0.
- Added foldseek 10.0.0 container recipe and registry.

Version 0.20.0 (April 2026)
----------------------------

**CLI & User Experience**

- Added a rich footer to ``damona --help`` with author, documentation,
  issues, and Zenodo links.
- Added a welcome box displayed on first ``damona`` invocation in each shell
  session (bash, zsh, fish).
- Removed redundant info from the help docstring and shell welcome message.
- Removed the debug message "Using Damona executable: …" from shell scripts.
- Improved ``damona search`` with fallback recommendation for bundled binaries.

**Registry & New Recipes**

- Added new recipes: spades 4.1.0, kallisto 0.51.1, pbmm2 1.16.99,
  STAR 2.7.11b, nextdenovo 2.5.2, deepvariant 1.10.0, diamond 2.1.24,
  pbsv 2.11.0, bamqc, idr 2.1.0, unicycler 0.5.1, bioconvert 1.2.0.
- Added ``broken`` flag to mark buggy releases (hidden from search but still
  installable).

**Documentation**

- Updated ``damona --help`` and ``damona search bwa`` screenshots in README
  and user guide.
- Fixed Sphinx warnings in ``doc/conf.py``: removed deprecated
  ``get_html_theme_path``, unsupported theme options, added ``sphinx_click``
  extension, updated ``source_suffix`` format.
- Updated and improved README files for individual recipes.

Version 0.19.2 (March 2026)
-----------------------------

- Faster ``damona check`` command.
- Added new recipe for LongReadSum.
- Bumped requests dependency to 2.33.0.

Version 0.19.1 (March 2026)
-----------------------------

- Renamed ``damona upload`` command to ``damona publish``.
- Added new recipes: minimap2, isoquant, busco 6.0.0.
- New Zenodo publishing strategy.

Version 0.18.0
--------------

- See git history for earlier changes.
