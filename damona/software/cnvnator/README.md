# CNVnator Container Recipes

Two recipe variants available for CNVnator v0.4.1:

## Primary: `Singularity.cnvnator_0.4.1` (conda-based, 906 MB)

**Status:** Published to Zenodo, QA-verified, pinned dependencies

Uses `micromamba` to install `cnvnator=0.4.1` and `samtools==1.10` from conda-forge/bioconda.

- Faster build (minutes, not hours)
- Simpler maintenance
- Fully tested and validated

## Alternative: `Singularity.cnvnator_0.4.1.source` (multi-stage source build, untested)

**Status:** Experimental, not published

Compiles CNVnator, samtools, htslib, and ROOT 6.32.08 from source using multi-stage Docker→Singularity conversion.

- Potentially smaller final image (multi-stage discards build artifacts)
- Complex ROOT/C++17 build chain
- **Not fully tested** — issues with ROOT headers and missing files (callbaf.py) remain unresolved
- Use only if you need source-compiled binaries or are willing to debug ROOT build configuration

**Recommendation:** Use `Singularity.cnvnator_0.4.1` for production. The `.source` variant is a proof-of-concept for future optimization but requires additional development.
