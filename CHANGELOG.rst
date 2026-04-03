Changelog
=========

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
