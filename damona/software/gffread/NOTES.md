**`gffread:0.12.7`'s micromamba install is unpinned** (`micromamba install
$OPTS gffread`, no `=version`). Rebuilding the recipe today installs gffread
0.12.9, not 0.12.7 (confirmed by rebuild-and-diff, 2026-08).

Not a deliberate "track latest" choice: the recipe was written assuming
whatever micromamba solved at the time matched the version being packaged,
and the registry key was set from that assumption rather than verified
against the installed binary afterwards.

The published 0.12.7 deposit is not known to be wrong -- it was presumably
built close to its claimed release and has not been independently checked
against the key, unlike a confirmed `mislabelled` case. What is known is that
the *recipe* does not reproduce it: rebuilt today it yields 0.12.9. Left
as-is rather than re-pinned.
