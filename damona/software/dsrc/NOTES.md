**`dsrc` prints `version: 2.02 @ 30.09.2014`, but this image contains the
upstream v2.0.2 release.** The odd version string is an upstream bug, not a
packaging mistake here.

The recipe builds from the tagged source archive:

```
VERSION="2.0.2"
wget https://github.com/refresh-bio/DSRC/archive/v${VERSION}.tar.gz
```

and that tag hard-codes a truncated version string in the C++ source:

```
refresh-bio/DSRC tag v2.0.2 -> src/main.cpp line 18:
    const std::string version = "2.02 @ 30.09.2014";
```

The date in that string (30.09.2014) also predates the v2.0.2 release, so the
constant was simply never refreshed between releases.

So the registry key 2.0.2 is correct and should not be "fixed" to match what the
tool prints. Any audit that compares a registry version against the binary's
banner will flag this container; the upstream tag and the pinned recipe are the
authoritative record here, not the binary's self-report.
