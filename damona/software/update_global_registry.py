#!/usr/bin/env python3
import glob
import os
from pathlib import Path

os.chdir(Path(__file__).parent)


files = glob.glob("*/registry.yaml")

with open("registry.yaml", "w") as fout:
    for filename in files:
        fout.write("# " + filename + "\n")
        with open(filename, "r") as data:
            fout.write(data.read() + "\n")

import subprocess

subprocess.run(["git", "add", "registry.yaml"], check=True)


N = len(files)
print(f"\u2714 Parsed {N} files and saved in registry.yaml")
