Here, multiqc also includes the Sequana modules.
We did a copy/paste of sequana 0.16.0 keeping only the multiqc modules
multiqc 0.16.0 is compatible with sequana.
multiqc 1.17 and above are not.


to include new sequana multiqc version,
- copy the 0.16.0 version,
    - copy the current multiqc direcyory of sequana to replace the existing one,
    - update requirements.txt to remove pin on multiqc version,
    - update version in the setup.py
