Changelog
=========

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
