**A release keyed 2.1.0 was delisted: it was never pbbam 2.1.0.** Its recipe set
`VERSION=2.3.0` and fetched the same `v2.3.0` tarball as the release that is
still listed, so the deposit was a duplicate 2.3.0 build uploaded by mistake,
and the tools inside reported 2.3.0. It added nothing over 2.3.0, so the entry
and its recipe are gone; the Zenodo deposit (record 7814654, md5
af5c1300e7eecb78e39ecca7e2f85a4c) remains valid and citable.

## The two recipes differed by one block, and it had no effect

The deleted `Singularity.pbbam_2.1.0` was `Singularity.pbbam_2.3.0` minus this:

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

The practical consequence is that the two images behaved identically -- which is
why the duplicate was worth deleting rather than keeping -- and that **2.3.0 has
no working chemistry-bundle support**: on a movie whose chemistry postdates the
compiled-in table it fails with "unsupported sequencing chemistry combination",
exactly as if no bundle had been shipped.

2.4.0 fixes it. The bundle lives in `/opt/smrt-chemistry` and the variable is
exported from `%environment`, so it is active without any caller setup:

```
$ singularity exec pbbam_2.4.0.img sh -c 'echo $SMRT_CHEMISTRY_BUNDLE_DIR'
/opt/smrt-chemistry
```

## Notes on the 2.4.0 build

Built from source on alpine, unlike its predecessors in three ways worth
keeping:

- **pbcopper is pinned to v2.3.0.** Upstream's `subprojects/pbcopper.wrap`
  tracks the pbcopper *develop branch*, so every rebuild of the old recipes
  produced a different container. Cloning the tag into `subprojects/pbcopper`
  makes the wrap inert.
- **`CXXFLAGS="-include cstdint"`.** pbcopper 2.3.0 predates GCC 13: its
  `cli2/OptionValue.h` uses `int8_t` and friends without including `<cstdint>`,
  which libstdc++ no longer provides transitively. Force-including it fixes
  every site without patching upstream sources.
- **Static linking.** The tools otherwise need `libpbbam.so` and
  `libpbcopper.so`, which exist only inside `builddir`. That is why the old
  images kept the entire ~200 MB build tree and pointed `PATH` at it; 2.4.0 is
  15.8 MB.

The chemistry table is pinned by pbcore commit rather than tag, because
pbcore's newest tag (2.6.0) predates the chemistries the bundle exists to
describe.
