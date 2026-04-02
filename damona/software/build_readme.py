import glob
import os
import sys

import packaging.version
import yaml


def split_binaries(binaries_spec):
    """Convert binaries spec (list or string) to a list.

    Handles both list and whitespace/comma-separated string formats.
    """
    if isinstance(binaries_spec, list):
        return binaries_spec
    elif isinstance(binaries_spec, str):
        return binaries_spec.replace(",", " ").split()
    else:
        return []


def get_release_binaries(software_name, software_data, version_data):
    """Resolve effective binaries for a specific release.

    Implements the same logic as Release._get_binaries() from registry.py:
    (global_binaries | release_binaries | extra_binaries) - exclude_binaries
    Falls back to software name if no binaries specified.
    """
    global_binaries = set(split_binaries(software_data.get("binaries", [])))
    release_binaries = set(split_binaries(version_data.get("binaries", [])))
    extra_binaries = set(split_binaries(version_data.get("extra_binaries", [])))
    exclude_binaries = set(split_binaries(version_data.get("exclude_binaries", [])))

    combined = (global_binaries | release_binaries | extra_binaries) - exclude_binaries

    if not combined:
        return [software_name]
    return sorted(combined)


def get_latest_version(releases_dict):
    """Return the latest version from a releases dict."""
    if not releases_dict:
        return None
    return max(releases_dict.keys(), key=lambda x: packaging.version.parse(x.split("-")[0]))


def parse_registry(yaml_file):
    """Parse the YAML registry file and return structured data."""
    with open(yaml_file, "r") as f:
        data = yaml.safe_load(f)
    return data


def generate_markdown(software_name, software_data):
    """Generate a Markdown README from software registry data."""
    markdown_content = f"# {software_name}\n\n"

    # DOI section (graceful if missing)
    doi = software_data.get("doi")
    if doi:
        markdown_content += f"**DOI:** [{doi}](https://doi.org/{doi})\n\n"

    releases = software_data.get("releases", {})

    # Global binaries list
    global_binaries = split_binaries(software_data.get("binaries", []))
    if not global_binaries:
        global_binaries = [software_name]

    markdown_content += "## Binaries\n\n"
    markdown_content += " ".join(f"`{b}`" for b in global_binaries) + "\n\n"

    # Installation section
    latest_version = get_latest_version(releases)
    markdown_content += "## Installation\n\n```bash\n"
    markdown_content += f"damona install {software_name}               # latest ({latest_version})\n"
    markdown_content += f"damona install {software_name}:VERSION        # specific version\n"
    markdown_content += "```\n\n"

    # Versions table
    markdown_content += "## Available Versions\n\n"
    markdown_content += "| Version | Size | Binaries | DOI |\n"
    markdown_content += "|---------|------|----------|-----|\n"

    # Sort versions by version number (handling special cases like x.y.z-py3)
    sorted_versions = sorted(releases.keys(), key=lambda x: packaging.version.parse(x.split("-")[0]), reverse=True)

    for version in sorted_versions:
        release = releases[version]

        # Version name with latest indicator
        version_label = version
        if version == latest_version:
            version_label = f"**{version}** *(latest)*"
        else:
            version_label = f"`{version}`"

        # Size
        filesize = release.get("filesize")
        if filesize and isinstance(filesize, (int, float)):
            size_mb = float(filesize) / (1024 * 1024)
            size_str = f"{size_mb:.2f} MB"
        else:
            size_str = "—"

        # Binaries
        release_binaries = get_release_binaries(software_name, software_data, release)
        binaries_str = " ".join(f"`{b}`" for b in release_binaries)

        # DOI
        release_doi = release.get("doi")
        if release_doi:
            doi_str = f"[{release_doi}](https://doi.org/{release_doi})"
        else:
            doi_str = "—"

        markdown_content += f"| {version_label} | {size_str} | {binaries_str} | {doi_str} |\n"

    return markdown_content


def update_all():
    """Generate README.md files for all software in the registry."""
    filenames = glob.glob("*/registry.yaml")

    for registry_file in sorted(filenames):
        software_name = registry_file.split("/")[0]

        try:
            registry_data = parse_registry(registry_file)
            # Each registry file has a single top-level key (the software name)
            if software_name not in registry_data:
                print(f"⚠ skipped {registry_file}: mismatched software name in YAML")
                continue

            software_data = registry_data[software_name]
            readme_content = generate_markdown(software_name, software_data)
        except Exception as e:
            print(f"⚠ skipped {registry_file}: {type(e).__name__}: {e}")
            continue

        outfile = f"{software_name}/README.md"

        # Check if update is needed
        to_alter = False
        if os.path.exists(outfile):
            with open(outfile, "r") as fin:
                existing_content = fin.read()
            if readme_content == existing_content:
                print(f"✓ skipped {registry_file}: unchanged")
                continue
            to_alter = True
        else:
            to_alter = True

        # Write the file
        if to_alter:
            with open(outfile, "w") as fout:
                fout.write(readme_content)
            print(f"✓ updated {outfile}")


if __name__ == "__main__":
    update_all()
