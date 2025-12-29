"""
TDD RED Phase: Tests for telegram_getter package setup.

These tests verify:
1. Package can be imported
2. __version__ is defined
3. CLI entry point is accessible
4. Environment variables can be loaded
"""

from pathlib import Path


class TestPackageImport:
    """Test that the package can be imported correctly."""

    def test_package_can_be_imported(self):
        """
        GIVEN the telegram_getter package is installed
        WHEN importing the package
        THEN no ImportError is raised
        """
        import telegram_getter

        assert telegram_getter is not None

    def test_version_is_defined(self):
        """
        GIVEN the telegram_getter package is installed
        WHEN accessing __version__
        THEN a version string is returned
        """
        from telegram_getter import __version__

        assert __version__ is not None
        assert isinstance(__version__, str)
        assert len(__version__) > 0

    def test_version_follows_semver_format(self):
        """
        GIVEN the telegram_getter package is installed
        WHEN accessing __version__
        THEN it follows semantic versioning (major.minor.patch)
        """
        from telegram_getter import __version__

        parts = __version__.split(".")
        assert len(parts) >= 2, "Version should have at least major.minor"
        # First two parts should be numeric
        assert parts[0].isdigit(), "Major version should be numeric"
        assert parts[1].isdigit(), "Minor version should be numeric"


class TestModuleStructure:
    """Test that all required modules exist."""

    def test_cli_module_exists(self):
        """
        GIVEN the telegram_getter package
        WHEN importing cli module
        THEN no ImportError is raised
        """
        from telegram_getter import cli

        assert cli is not None

    def test_auth_module_exists(self):
        """
        GIVEN the telegram_getter package
        WHEN importing auth module
        THEN no ImportError is raised
        """
        from telegram_getter import auth

        assert auth is not None

    def test_downloader_module_exists(self):
        """
        GIVEN the telegram_getter package
        WHEN importing downloader module
        THEN no ImportError is raised
        """
        from telegram_getter import downloader

        assert downloader is not None

    def test_exporter_module_exists(self):
        """
        GIVEN the telegram_getter package
        WHEN importing exporter module
        THEN no ImportError is raised
        """
        from telegram_getter import exporter

        assert exporter is not None

    def test_utils_module_exists(self):
        """
        GIVEN the telegram_getter package
        WHEN importing utils module
        THEN no ImportError is raised
        """
        from telegram_getter import utils

        assert utils is not None


class TestCLIEntryPoint:
    """Test CLI entry point accessibility."""

    def test_cli_main_function_exists(self):
        """
        GIVEN the telegram_getter.cli module
        WHEN accessing the main function
        THEN main function is callable
        """
        from telegram_getter.cli import main

        assert callable(main)

    def test_main_module_is_runnable(self):
        """
        GIVEN the telegram_getter package
        WHEN __main__.py exists
        THEN the package can be run as a module
        """
        import telegram_getter.__main__

        assert telegram_getter.__main__ is not None


class TestEnvironmentConfig:
    """Test environment configuration handling."""

    def test_env_example_file_exists(self):
        """
        GIVEN the project structure
        WHEN looking for .env.example
        THEN the file exists with required placeholders
        """
        env_example = Path(__file__).parent.parent / ".env.example"
        assert env_example.exists(), ".env.example file should exist"

        content = env_example.read_text()
        assert "API_ID" in content, ".env.example should have API_ID placeholder"
        assert "API_HASH" in content, ".env.example should have API_HASH placeholder"

    def test_utils_has_load_config_function(self):
        """
        GIVEN the telegram_getter.utils module
        WHEN accessing load_config function
        THEN the function exists and is callable
        """
        from telegram_getter.utils import load_config

        assert callable(load_config)

    def test_load_config_returns_dict(self):
        """
        GIVEN no .env file exists
        WHEN calling load_config
        THEN returns a dict with None values for missing keys
        """
        from telegram_getter.utils import load_config

        config = load_config()
        assert isinstance(config, dict)
        assert "api_id" in config
        assert "api_hash" in config
