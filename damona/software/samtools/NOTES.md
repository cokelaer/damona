# samtools 1.20.0 build notes

- The registry key is 1.20.0; the binary reports "samtools 1.20" (upstream drops the trailing .0).
- Only the base image tag (alpine:3.20) is pinned. apk packages (runtime libs and build deps) are not pinned
  individually, because Alpine keeps only the current version of each package per branch, so a pinned
  `pkg=X.Y.Z-rN` would break builds as soon as the branch updates. samtools itself is built from the pinned tarball.
- The tarball sha256 in the recipe was computed from the HTTPS release asset. Upstream publishes no checksum
  for it (the release lists only the tarball), so the check is trust-on-first-use: it detects later changes to
  the asset, not an initially tampered one.
