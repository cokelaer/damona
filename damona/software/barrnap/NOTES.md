**`barrnap --version` reports 1.10.5, but this image really does contain
1.10.6.** The discrepancy is an upstream bug, not a packaging mistake here.

The recipe pins the package explicitly:

```
micromamba install -c conda-forge -c bioconda -n main -y barrnap=1.10.6 "hmmer>=3.1"
```

and the installed package inside the image is `barrnap-1.10.6-pl5321hdfd78af_0`
(see `/opt/conda/envs/main/conda-meta/`). The version string printed at runtime
comes from a constant hard-coded in the Perl script, and upstream tagged v1.10.6
without bumping it:

```
tseemann/barrnap tag v1.10.6 -> bin/barrnap line 17: my $VERSION = "1.10.5";
tseemann/barrnap tag v1.10.5 -> bin/barrnap line 17: my $VERSION = "1.10.5";
```

So the registry key 1.10.6 is correct and should not be "fixed" to match what
the tool prints. Any audit that compares a registry version against
`--version` output will flag this container; the package metadata and the
pinned recipe are the authoritative record here, not the binary's self-report.
