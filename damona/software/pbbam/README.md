# pbbam

**DOI:** [10.5281/zenodo.7814653](https://doi.org/10.5281/zenodo.7814653)

## Binaries

`bam2sam` `pbmerge` `pbbamify` `pbindex` `pbindexdump` `ccs-kinetics-bystrandify`

## Installation

```bash
damona install pbbam               # latest (2.4.0)
damona install pbbam:VERSION        # specific version
```

## Available Versions

| Version | Size | Binaries | DOI |
|---------|------|----------|-----|
| **2.4.0** *(latest)* | 15.10 MB | `bam2sam` `ccs-kinetics-bystrandify` `pbbamify` `pbindex` `pbindexdump` `pbmerge` | [10.5281/zenodo.21986315](https://doi.org/10.5281/zenodo.21986315) |

## Notes

pbbam ships the PacBio BAM command line tools; this image builds all six of
them from source and adds a chemistry bundle, which upstream leaves to the
caller.

## Chemistry bundle

pbbam maps the PacBio chemistry triplet (BindingKit, SequencingKit,
BasecallerVersion) to a chemistry name using a table compiled into the binary.
A movie produced with a chemistry newer than that table fails with
"unsupported sequencing chemistry combination" unless a bundle is supplied.

pbbam looks the bundle up at runtime, in
`$SMRT_CHEMISTRY_BUNDLE_DIR/chemistry.xml` (`src/ChemistryTable.cpp`):

```c
const char* pth = std::getenv("SMRT_CHEMISTRY_BUNDLE_DIR");
if (pth != nullptr && pth[0] != '\0') { chemPath = pth; }
else { return empty; }
...
auto tbl = ChemistryTableFromXml(chemPath + "/chemistry.xml");
```

If the variable is unset it silently falls back to the empty table, so a missing
bundle looks like a data problem rather than a configuration one. The bundle is
baked into `/opt/smrt-chemistry` here and the variable is exported from
`%environment`, so it is active without any caller setup:

```
$ singularity exec pbbam_2.4.0.img sh -c 'echo $SMRT_CHEMISTRY_BUNDLE_DIR'
/opt/smrt-chemistry
```

**The export must stay in `%environment`.** Putting it in `%post` looks
equivalent and is not: `%post` variables are gone once the build ends, the
runtime lookup then returns `nullptr`, and the bundle becomes dead weight that
is downloaded and never read. `%test` guards against that by asserting the file
is reachable through the variable and carries the `MappingTable` root node
pbbam requires.

## Build notes

Built from source on alpine. Three decisions worth keeping on the next bump:

- **pbcopper is pinned to v2.3.0.** Upstream's `subprojects/pbcopper.wrap`
  tracks the pbcopper *develop branch*, which would make every rebuild produce a
  different container. Cloning the tag into `subprojects/pbcopper` makes the
  wrap inert, since meson prefers an existing subproject directory over the
  `.wrap` file.
- **`CXXFLAGS="-include cstdint"`.** pbcopper 2.3.0 predates GCC 13: its
  `cli2/OptionValue.h` uses `int8_t` and friends without including `<cstdint>`,
  which libstdc++ no longer provides transitively, and alpine now ships GCC 15.
  Force-including the header fixes every such site without patching upstream
  sources, which a pbcopper bump would otherwise invalidate.
- **Static linking** (`--default-library=static`). The tools otherwise need
  `libpbbam.so` and `libpbcopper.so`, which exist only inside `builddir`, so the
  build tree cannot be deleted -- the difference between a 15.8 MB image and a
  213 MB one.

htslib comes from the hash-pinned wrap shipped in the pbbam tarball (1.17)
rather than from the distribution, so the build does not drift with the alpine
release. The chemistry table is pinned by pbcore commit rather than tag, because
pbcore's newest tag (2.6.0) predates the chemistries the bundle exists to
describe.
