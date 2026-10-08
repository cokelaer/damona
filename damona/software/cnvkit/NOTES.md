## Notes

- CNVkit 0.9.10 is built from the upstream git tag `v0.9.10`; runtime dependencies come from conda-forge/bioconda, pinned.
- `scripts/snpfilter.sh` from the upstream source is **not shipped**. It relies on `samtools mpileup --VCF`, which no longer exists in the pinned samtools 1.17, so the script cannot run in this container.
- `pip` and `git` are installed only as build tools (pinned); `git` is removed at the end of the build.
