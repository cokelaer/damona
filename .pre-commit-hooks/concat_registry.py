#!/usr/bin/env python3

import glob
import os
import subprocess

BASE_DIR = "damona/software"
OUTPUT_FILE = os.path.join(BASE_DIR, "registry.yaml")


def concatenate_registry():
    registry_files = sorted(glob.glob(f"{BASE_DIR}/*/registry.yaml"))

    with open(OUTPUT_FILE, "w") as outfile:
        for file in registry_files:
            with open(file, "r") as infile:
                outfile.write(f"# {file}\n")  # Add comment indicating the source
                outfile.write(infile.read() + "\n")  # Append content with newline

    subprocess.run(["git", "add", OUTPUT_FILE])


if __name__ == "__main__":
    concatenate_registry()
