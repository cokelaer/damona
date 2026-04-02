"""Tests for damona/software/build_readme.py."""

import os

import yaml

SAMPLE_REGISTRY_DATA = {
    "bwa": {
        "doi": "10.5281/zenodo.7736676",
        "releases": {
            "0.7.17": {
                "download": "https://zenodo.org/record/7970243/files/bwa_0.7.17.img",
                "md5sum": "d538df257a4f1e3ab313de57dee5ccf3",
                "doi": "10.5281/zenodo.7970243",
                "filesize": 9392128,
                "binaries": "bwa",
            }
        },
        "binaries": "bwa",
    }
}


def test_parse_registry(tmp_path):
    """parse_registry reads a YAML file and returns the expected dict."""
    from damona.software.build_readme import parse_registry

    registry_file = tmp_path / "registry.yaml"
    with open(registry_file, "w") as f:
        yaml.dump(SAMPLE_REGISTRY_DATA, f)

    result = parse_registry(str(registry_file))

    assert "bwa" in result
    assert result["bwa"]["doi"] == "10.5281/zenodo.7736676"
    assert "0.7.17" in result["bwa"]["releases"]


def test_generate_markdown_content():
    """generate_markdown produces the expected Markdown sections."""
    from damona.software.build_readme import generate_markdown

    # Extract software name and data (generate_markdown takes name and data separately)
    software_name = "bwa"
    software_data = SAMPLE_REGISTRY_DATA[software_name]
    md = generate_markdown(software_name, software_data)

    assert "# bwa" in md
    assert "10.5281/zenodo.7736676" in md
    assert "0.7.17" in md
    assert "10.5281/zenodo.7970243" in md  # release DOI
    # 9392128 bytes / (1024*1024) ≈ 8.96 MB
    assert "8.96 MB" in md
    assert "## Binaries" in md
    assert "## Installation" in md
    assert "## Available Versions" in md
    assert "`bwa`" in md


def test_generate_markdown_no_binaries():
    """generate_markdown handles releases and tools without a binaries field."""
    from damona.software.build_readme import generate_markdown

    software_name = "tool"
    software_data = {
        "doi": "10.1234/test",
        "releases": {
            "1.0.0": {
                "download": "https://example.com/tool_1.0.0.img",
                "md5sum": "abc123",
                "doi": "10.1234/test.v1",
                "filesize": 1048576,
            }
        },
    }

    md = generate_markdown(software_name, software_data)

    assert "# tool" in md
    assert "1.0.0" in md
    assert "1.00 MB" in md
    # No binaries specified, should show the tool name as default binary
    assert "`tool`" in md


def test_update_all_creates_readme(tmp_path):
    """update_all writes a README.md when none exists."""
    from damona.software import build_readme

    # Directory name must match the software name in the registry YAML
    sub_dir = tmp_path / "bwa"
    sub_dir.mkdir()

    registry_file = sub_dir / "registry.yaml"
    with open(registry_file, "w") as f:
        yaml.dump(SAMPLE_REGISTRY_DATA, f)

    old_cwd = os.getcwd()
    try:
        os.chdir(tmp_path)
        build_readme.update_all()
    finally:
        os.chdir(old_cwd)

    readme = sub_dir / "README.md"
    assert readme.exists()
    content = readme.read_text()
    assert "# bwa" in content


def test_update_all_skips_unchanged(tmp_path, capsys):
    """update_all prints 'skipped … unchanged' when the README is already up to date."""
    from damona.software import build_readme

    # Directory name must match the software name in the registry YAML
    sub_dir = tmp_path / "bwa"
    sub_dir.mkdir()

    registry_file = sub_dir / "registry.yaml"
    with open(registry_file, "w") as f:
        yaml.dump(SAMPLE_REGISTRY_DATA, f)

    old_cwd = os.getcwd()
    try:
        os.chdir(tmp_path)
        build_readme.update_all()  # first run – creates README
        build_readme.update_all()  # second run – should skip
    finally:
        os.chdir(old_cwd)

    captured = capsys.readouterr()
    assert "unchanged" in captured.out


def test_update_all_updates_changed_readme(tmp_path, capsys):
    """update_all overwrites README.md when the content has changed."""
    from damona.software import build_readme

    # Directory name must match the software name in the registry YAML
    sub_dir = tmp_path / "bwa"
    sub_dir.mkdir()

    registry_file = sub_dir / "registry.yaml"
    with open(registry_file, "w") as f:
        yaml.dump(SAMPLE_REGISTRY_DATA, f)

    readme = sub_dir / "README.md"
    readme.write_text("stale content")

    old_cwd = os.getcwd()
    try:
        os.chdir(tmp_path)
        build_readme.update_all()
    finally:
        os.chdir(old_cwd)

    new_content = readme.read_text()
    assert "stale content" not in new_content
    assert "# bwa" in new_content


def test_update_all_handles_parse_error(tmp_path, capsys):
    """update_all skips registry files whose content cannot be rendered."""
    from damona.software import build_readme

    sub_dir = tmp_path / "broken_tool"
    sub_dir.mkdir()

    # YAML null → None, which causes generate_markdown to fail when iterating
    registry_file = sub_dir / "registry.yaml"
    registry_file.write_text("null\n")

    old_cwd = os.getcwd()
    try:
        os.chdir(tmp_path)
        build_readme.update_all()  # must not raise
    finally:
        os.chdir(old_cwd)

    captured = capsys.readouterr()
    assert "skipped" in captured.out
