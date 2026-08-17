**`fastANI --version` reports `version 1.33`, but this image really does contain
1.34.** Upstream shipped the v1.34 release without bumping the version constant,
so the binary misreports itself.

The recipe takes the official pre-built release artifact:

```
wget https://github.com/ParBLiSS/FastANI/releases/download/v1.34/fastANI-linux64-v1.34.zip
```

and the binary inside the image is byte-identical to the one in that zip:

```
image /usr/local/bin/fastANI            md5 ae2974b3987899aa42f5de8c0cd27911
upstream fastANI-linux64-v1.34.zip      md5 ae2974b3987899aa42f5de8c0cd27911
upstream fastANI-Linux64-v1.33.zip      md5 6bdd6c185c65206647fe92af18d448d0
```

The v1.33 and v1.34 artifacts are different binaries, yet both print
`version 1.33` — the only string matching `1.3[0-9]` in either executable. So
the stale constant is upstream's, not a case of the wrong archive being
downloaded.

So the registry key 1.34.0 is correct and should not be "fixed" to 1.33. Any
audit that compares a registry version against `--version` output will flag this
container; the pinned release URL and the md5 above are the authoritative record
here, not the binary's self-report.
