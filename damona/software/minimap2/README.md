# minimap2

**DOI:** [10.5281/zenodo.5799480](https://doi.org/10.5281/zenodo.5799480)

## Binaries

`minimap2`

## Installation

```bash
damona install minimap2               # latest (2.28.0)
damona install minimap2:VERSION        # specific version
```

## Available Versions

| Version | Size | Binaries | DOI |
|---------|------|----------|-----|
| **2.28.0** *(latest)* | 4.50 MB | `minimap2` | [10.5281/zenodo.23326293](https://doi.org/10.5281/zenodo.23326293) |
| `2.24.0` | 6.73 MB | `minimap2` | [10.5281/zenodo.7817800](https://doi.org/10.5281/zenodo.7817800) |
| `2.23.0` | 36.32 MB | `minimap2` | [10.5281/zenodo.5799482](https://doi.org/10.5281/zenodo.5799482) |
| `2.17.0` | 37.39 MB | `minimap2` | [10.5281/zenodo.5799481](https://doi.org/10.5281/zenodo.5799481) |

## Notes

## minimap2 2.28.0

- The binary is the upstream prebuilt x64-linux release (v2.28, `minimap2-2.28_x64-linux.tar.bz2`), verified by SHA256 in the recipe. It reports `2.28-r1209`.
- apk packages (`bash`, `libc6-compat`) are not pinned beyond the `alpine:3.20` base image tag.
