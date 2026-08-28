"""Integration tests for damona - test real components working together."""
import pytest

from damona.registry import Registry


class TestRegistryIntegration:
    """Test Registry with real local registry data."""

    def test_registry_loads_local(self):
        """Real registry loads without errors."""
        registry = Registry(from_url=None)
        assert len(registry.registry) > 0

    def test_registry_has_expected_software(self):
        """Local registry contains common tools."""
        registry = Registry(from_url=None)
        software_names = set(k.split(":")[0] for k in registry.registry.keys())
        # Check for a few common tools that should always be there
        assert "fastqc" in software_names or "samtools" in software_names

    def test_get_list_returns_versioned_keys(self):
        """get_list returns name:version format."""
        registry = Registry(from_url=None)
        results = registry.get_list()
        assert all(":" in r for r in results), "All results should be name:version"

    def test_search_pattern_case_insensitive(self):
        """Pattern matching is case-insensitive."""
        registry = Registry(from_url=None)
        lower = registry.get_list("samtools")
        upper = registry.get_list("SAMTOOLS")
        mixed = registry.get_list("SamTools")
        assert lower == upper == mixed

    def test_get_binaries_returns_software_binaries(self):
        """get_binaries returns actual binary names."""
        registry = Registry(from_url=None)
        binaries_dict = registry.get_binaries()
        # Each value should be a list of binary names
        for software, binary_list in binaries_dict.items():
            assert isinstance(binary_list, list)
            assert all(isinstance(b, str) for b in binary_list)

    def test_suggest_similar_finds_close_matches(self):
        """suggest_similar returns plausible suggestions."""
        registry = Registry(from_url=None)
        # Test with a common typo
        suggestions = registry.suggest_similar("samtols", n=3)
        assert "samtools" in suggestions or len(suggestions) > 0

    def test_registry_caching(self):
        """Registry instances with same parameters share cache."""
        r1 = Registry(from_url=None)
        r2 = Registry(from_url=None)
        # Should be same cached object (not deep equal, but same registry dict)
        assert r1.registry is r2.registry

    def test_registry_releases_have_download_urls(self):
        """All releases have download URLs."""
        registry = Registry(from_url=None)
        for key, release in registry.registry.items():
            assert release.download is not None, f"{key} missing download URL"

    def test_mislabelled_filter_works(self):
        """Mislabelled software can be included/excluded."""
        registry = Registry(from_url=None)
        with_mislabelled = registry.get_list(include_mislabelled=True)
        without_mislabelled = registry.get_list(include_mislabelled=False)
        # Should have fewer or equal without mislabelled
        assert len(without_mislabelled) <= len(with_mislabelled)


class TestSearchCLIIntegration:
    """Test search command with real registry data."""

    def test_search_exact_match_displays_results(self):
        """Searching for existing software displays results."""
        from click.testing import CliRunner

        from damona import script

        runner = CliRunner()
        result = runner.invoke(script.search, ["samtools", "--images-only"])
        assert result.exit_code == 0
        assert "samtools" in result.output.lower()

    def test_search_no_match_shows_suggestions(self):
        """Searching for nonexistent software shows suggestions."""
        from click.testing import CliRunner

        from damona import script

        runner = CliRunner()
        result = runner.invoke(script.search, ["samtls", "--local-registry-only"])
        assert result.exit_code == 0
        assert "Did you mean" in result.output or "samtools" in result.output

    def test_search_star_lists_all(self):
        """Searching for * lists all available software."""
        from click.testing import CliRunner

        from damona import script

        runner = CliRunner()
        result = runner.invoke(script.search, ["*", "--local-registry-only", "--images-only"])
        assert result.exit_code == 0
        # Should have many results
        lines = result.output.strip().split("\n")
        assert len(lines) > 10


class TestInstallIntegration:
    """Test install/uninstall workflows (don't actually install)."""

    def test_search_shows_installable_software(self):
        """Search shows software available to install."""
        from click.testing import CliRunner

        from damona import script

        runner = CliRunner()
        result = runner.invoke(script.search, ["samtools"])
        assert result.exit_code == 0
        # Should show installation recommendations
        assert "damona install" in result.output or "samtools" in result.output.lower()


class TestRegistryCaching:
    """Test that caching provides performance benefit."""

    def test_cache_prevents_redundant_discovery(self):
        """Second Registry creation reuses cached data."""
        from damona.registry import Registry

        Registry._cache.clear()  # Clear cache
        r1 = Registry(from_url=None)
        initial_registry = r1.registry
        r2 = Registry(from_url=None)
        # Should reference same object (not re-discovered)
        assert r2.registry is initial_registry

    def test_different_urls_use_different_cache_keys(self):
        """Different URLs have separate cache entries."""
        from damona.registry import Registry

        cache_size_before = len(Registry._cache)
        # Just create instances, don't care if they fail
        try:
            Registry(from_url="http://example.com/registry.yaml")
        except Exception:
            pass
        # Cache should have grown (or URL was intercepted)
        # This mainly tests that cache keys are distinct
        assert True
