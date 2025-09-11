import os
import sys

import yaml


def parse_registry(yaml_file):
    """Parse the YAML registry file and return structured data."""
    with open(yaml_file, "r") as f:
        data = yaml.safe_load(f)
    return data


def generate_markdown(registry_data):
    """Generate a Markdown README from parsed registry data."""
    markdown_content = ""

    for recipe, details in registry_data.items():
        markdown_content += f"# {recipe}\n\n"
        markdown_content += f"**DOI:** [{details['doi']}](https://doi.org/{details['doi']})\n\n"

        markdown_content += "## Available Versions\n"

        for version, release in details.get("releases", {}).items():
            size_mb = int(release.get("filesize", 0)) / (1024 * 1024)
            markdown_content += f"- **Version {version}**\n"
            markdown_content += f"  - [Download]({release['download']})\n"
            markdown_content += f"  - **MD5:** `{release['md5sum']}`\n"
            markdown_content += f"  - **DOI:** [{release['doi']}](https://doi.org/{release['doi']})\n"
            markdown_content += f"  - **Size:** {size_mb:.2f} MB\n"
            markdown_content += f"  - **Binaries:** {len(release.get('binaries', '').split())} available\n\n"

        # Global binary list
        binaries = details.get("binaries", "").split()
        markdown_content += f"## Binaries ({len(binaries)} total)\n\n"
        markdown_content += "```" + " ".join(binaries) + "```\n"

    return markdown_content


def update_all():

    import glob

    filenames = glob.glob("*/registry.yaml")

    for registry_file in sorted(filenames):
        registry_data = parse_registry(registry_file)
        try:
            readme_content = generate_markdown(registry_data)
        except:
            print(f"skipped {registry_file} : cannot parse")
            continue

        outfile = registry_file.split("/")[-2] + "/README.md"

        to_alter = False
        if os.path.exists(outfile):
            with open(outfile, "r") as fin:
                data = fin.read()
            if readme_content == data:
                print(f"skipped {registry_file} unchanged")
            else:
                to_alter = True
        else:
            to_alter = True
        # change only if requested
        if to_alter:
            with open(outfile, "w") as fout:
                fout.write(readme_content)
                print(f"Created/Updated README files generated and saved to {outfile}")


update_all()
