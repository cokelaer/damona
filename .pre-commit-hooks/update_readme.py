#!/usr/bin/env python3
"""Update README.rst with current registry statistics."""
import re
from datetime import datetime
from pathlib import Path

import yaml

# Navigate to the project root
root = Path(__file__).parent.parent

# Load the global registry
registry_path = root / "damona" / "software" / "registry.yaml"
readme_path = root / "README.rst"

with open(registry_path) as f:
    registry = yaml.safe_load(f)

# Count statistics
num_containers = len(registry)
num_versions = sum(len(software.get("releases", {})) for software in registry.values())

# Count unique binaries across all releases
unique_binaries = set()
for software in registry.values():
    binaries_str = software.get("binaries", "")
    if binaries_str:
        # Split by whitespace and add to set
        unique_binaries.update(binaries_str.split())

num_binaries = len(unique_binaries)

# Current date
current_date = datetime.now().strftime("%b. %Y")

# Read the README
with open(readme_path) as f:
    readme_content = f.read()

# Update the statistics note
# Pattern matches: "As of <date>, **Damona** ships <N> containers (<M> versions), providing <K> unique ready-to-use binaries."
# Use DOTALL flag to match across newlines in the note
pattern = (
    r"As of .+?, \*\*Damona\*\* ships \d+ containers \(\d+ versions\),\s+"
    r"providing \*\*\d+ unique ready-to-use binaries\*\*\."
)
replacement = (
    f"As of {current_date}, **Damona** ships {num_containers} containers "
    f"({num_versions} versions),\n           providing **{num_binaries} unique ready-to-use binaries**."
)

new_readme = re.sub(pattern, replacement, readme_content, flags=re.DOTALL)

# Write back
with open(readme_path, "w") as f:
    f.write(new_readme)

# Stage the file
import subprocess

subprocess.run(["git", "add", "README.rst"], check=True)

print(f"✔ Updated README: {num_containers} containers, {num_versions} versions, {num_binaries} binaries")
