**None of the three fastp releases (0.23.2, 0.23.3, 1.0.1) pin their source.**
The recipe `wget`s `http://opengene.org/fastp/fastp` -- upstream's own
always-latest static binary, with no version in the URL. Rebuilding any of
these three recipes today produces the same file: fastp 1.3.6, whatever
upstream currently publishes at that path (confirmed by rebuild-and-diff,
2026-08).

This was not a deliberate "track latest" choice: the recipe was written
assuming the binary at that URL matched the version being packaged at the
time, and the registry key was set from that assumption rather than verified
against the binary afterwards. bioconda does carry pinned fastp builds
(`fastp=1.0.1`, `fastp=0.23.3`, `fastp=0.23.2` all exist), so this was
avoidable.

The three published deposits are not known to be wrong -- each was presumably
built close to its claimed release and its content has not been independently
checked against the key, unlike a confirmed `mislabelled` case. What is known
is that the *recipe* does not reproduce them: rebuilt today, all three
recipes are identical and all three yield 1.3.6. Left as-is rather than
re-pinned; a future release under the `X.Y.Z-N` convention (see `dev.rst`)
would fix it without touching these deposits.
