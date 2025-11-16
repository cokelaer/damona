Difference from version to version.


From sequana 0.19.4, we version the container based on the date rather than sequana version.

25.11.15: uses sequana 0.19.5



Some versions are missing because we tend to match to the current sequana version.

0.19.3. new version. make sure sequana_coverage works
0.19.1 revamp. restart from micromamba. removed igvtools, rnaseqc, trinity, transdecoder that have their own container. bowtie2 fails  
0.15.1. same as 0.14.5 but with sequana 0.15.1 and snpEff 5.1d
0.14.5: same as 0.14.3 but with sequana 0.14.5
0.14.3: added openjdk>=11 for picard to work
0.14.2: updated ruamel_yaml; NEWS: seqkit  seqtk nanopolish; rust for gseapy required by Sequana
0.14.1: added  trinity transdecoder trinotate hmmer and sra-tools
0.12.0 add shustring in recipes and  fix bam_stats.py to bam_stat.py in registry
0.10.0 depends on conda 4.9.2  +falco -cufflinks(not available for py3.7)
0.9.0 depends on conda 4.7


to test:
- sequana_taxonomy --help /ktImportText PyQt5
