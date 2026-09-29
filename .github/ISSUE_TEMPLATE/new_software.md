---
name: New software container
about: Propose a new software (or new versions of an existing one) for Damona
title: 'New container: <software> <version(s)>'
labels: New recipes
assignees: ''
type: Feature

---

**Software**
- Name:
- Requested version(s) (exact, e.g. `4.5.0.0`):
- Homepage / source repository:
- License:
- Category (e.g. variant calling, QC, aligner):

**Why is it needed?**
Who uses it and where (e.g. nf-core pipelines, sequana, a publication). Link evidence if available.
Not already covered by an existing Damona container (checked with `damona search <name>` and the multi-tool containers, e.g. `ucsc`)?

**Installation / build hints**
- Preferred source: bioconda / PyPI / GitHub release tarball / other:
- Package or download URL for each requested version (must be version-pinned):
- Runtime dependencies (Java, Python, R, ...):
- Binaries to expose (executables users will call):
- A command that prints the version, for the `%test` section (e.g. `tool --version`):

**Checklist (for the person building it)**
- [ ] `damona/software/<name>/Singularity.<name>_X.Y.Z` with every input pinned (packages, URLs, base image tag)
- [ ] `%test` asserts the version
- [ ] Build with `damona build`, QA with the test script
- [ ] Publish to Zenodo, `registry.yaml` filled (URL, MD5, DOI, size, binaries)
- [ ] README generated, changelog updated

**Additional context**
Anything else (image size concerns, licensing restrictions, known build problems, alternative tools).
