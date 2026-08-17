**The release keyed 2.1.0 is not pbbam 2.1.0.** It is a second build of 2.3.0,
uploaded to Zenodo by mistake. `Singularity.pbbam_2.1.0` sets `VERSION=2.3.0`
like its sibling, fetches the same `v2.3.0` tarball, and the tools inside report
2.3.0. The deposit is permanent, so the entry is kept but flagged
`mislabelled`: installable by explicit version, hidden from search and from this
README.

## The two recipes differ by one block, and it has no effect

`Singularity.pbbam_2.3.0` additionally does:

```
cd /pbbam-${VERSION} && mkdir chemistry \
  && wget .../pbcore/chemistry/resources/mapping.xml -O chemistry.xml
export SMRT_CHEMISTRY_BUNDLE_DIR="${PWD}"
```

The intent is to teach pbbam about PacBio chemistry triplets newer than those
compiled into the binary; without a bundle, recent movies fail with
"unsupported sequencing chemistry combination". pbbam looks the bundle up at
runtime (`src/ChemistryTable.cpp`):

```c
const char* pth = std::getenv("SMRT_CHEMISTRY_BUNDLE_DIR");
if (pth != nullptr && pth[0] != '\0') { chemPath = pth; }
else { return empty; }
...
auto tbl = ChemistryTableFromXml(chemPath + "/chemistry.xml");
```

The export is in `%post`, not `%environment`, and `%post` variables do not
survive into the runtime image. So `getenv` returns `nullptr`, pbbam returns the
empty table, and the downloaded `chemistry.xml` is never read. (`mkdir
chemistry` is a leftover too: the file is written next to that directory, not
into it.)

The practical consequence is that the two images behave identically, and that
neither of them actually has chemistry-bundle support. Fixing it needs
`export SMRT_CHEMISTRY_BUNDLE_DIR=/pbbam-2.3.0` in `%environment` (the directory
holding `chemistry.xml`) and a rebuild.
