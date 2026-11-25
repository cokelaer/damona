UCHIME 4.2.40 is the last public-domain standalone release (source frozen at 4.2 by the
author; later chimera detection lives in the closed-source USEARCH). The binary reports
`uchime v4.2.40`, which is the registry key.

The recipe builds from the pinned source tarball (sha256 verified in `%post`) with
`-std=gnu++98`, because the 2011 code does not compile under newer C++ standards. The
upstream `mk` script is not used (it writes to `/dev/tty`). The base image is pinned to
`alpine:3.22`, but the `apk` packages (`g++`, `wget` for the build, `bash` kept at runtime)
are not individually pinned; the tarball checksum and the `%test` version assertion catch
any drift. The binary is static, so nothing else is needed at runtime.

UCHIME writes its banner and progress to stderr on every run.
