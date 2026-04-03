#!/usr/bin/env python3
import glob
import os
import subprocess
from pathlib import Path

os.chdir(Path(__file__).parent)

OUTPUT_FILE = "registry.yaml"

# Read current content
current = Path(OUTPUT_FILE).read_text() if Path(OUTPUT_FILE).exists() else ""

files = sorted(glob.glob("*/registry.yaml"))

lines = []
for filename in files:
    lines.append("# " + filename)
    # Strip trailing whitespace from each line and strip trailing blank lines
    content = Path(filename).read_text()
    for line in content.splitlines():
        lines.append(line.rstrip())
    lines.append("")  # blank line between sections

# Produce a single trailing newline (satisfies end-of-file-fixer)
new_content = "\n".join(lines).rstrip("\n") + "\n"

N = len(files)
print(f"\u2714 Parsed {N} files and saved in {OUTPUT_FILE}")

if new_content == current:
    raise SystemExit(0)

Path(OUTPUT_FILE).write_text(new_content)
subprocess.run(["git", "add", OUTPUT_FILE], check=True)
print("registry.yaml was updated and staged. Please re-run: git commit")
raise SystemExit(1)
