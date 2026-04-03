"""Tests for damona/software/update_global_registry.py."""

import shutil
import subprocess
import sys
from pathlib import Path


def test_update_global_registry(tmp_path):
    """update_global_registry.py aggregates sub-directory registry.yaml files."""
    # Copy the script into a temporary directory so that Path(__file__).parent
    # resolves to tmp_path, and glob("*/registry.yaml") finds our fixtures.
    script_src = Path(__file__).parent.parent / "damona" / "software" / "update_global_registry.py"
    script_dst = tmp_path / "update_global_registry.py"
    shutil.copy(str(script_src), str(script_dst))

    # Create one subdirectory with a registry.yaml
    sub_dir = tmp_path / "mytool"
    sub_dir.mkdir()
    (sub_dir / "registry.yaml").write_text("mytool:\n  doi: 10.5281/test\n")

    # Initialise a git repo so that "git add" succeeds
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )

    result = subprocess.run(
        [sys.executable, str(script_dst)],
        capture_output=True,
        text=True,
        cwd=tmp_path,
    )

    assert result.returncode in (0, 1), f"Script failed:\n{result.stderr}"
    assert "Parsed" in result.stdout
    assert "1" in result.stdout

    registry = tmp_path / "registry.yaml"
    assert registry.exists()
    content = registry.read_text()
    assert "mytool" in content
    assert "# mytool/registry.yaml" in content
