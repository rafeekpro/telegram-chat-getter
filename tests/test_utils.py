"""
TDD RED Phase: Tests for telegram_getter.utils module.

These tests verify utility functions work correctly.
"""


class TestLoadConfig:
    """Test the load_config utility function."""

    def test_load_config_with_env_file(self, tmp_path, monkeypatch):
        """
        GIVEN a .env file with API_ID and API_HASH
        WHEN calling load_config with that directory
        THEN returns config dict with values from .env
        """
        from telegram_getter.utils import load_config

        # Create temporary .env file
        env_file = tmp_path / ".env"
        env_file.write_text("API_ID=12345\nAPI_HASH=abcdef123456\n")

        # Change to temp directory
        monkeypatch.chdir(tmp_path)

        config = load_config()

        assert config["api_id"] == "12345"
        assert config["api_hash"] == "abcdef123456"

    def test_load_config_without_env_file(self, tmp_path, monkeypatch):
        """
        GIVEN no .env file exists
        WHEN calling load_config
        THEN returns config dict with None values
        """
        from telegram_getter.utils import load_config

        # Change to temp directory without .env
        monkeypatch.chdir(tmp_path)

        # Clear any existing env vars
        monkeypatch.delenv("API_ID", raising=False)
        monkeypatch.delenv("API_HASH", raising=False)

        config = load_config()

        assert config["api_id"] is None
        assert config["api_hash"] is None

    def test_load_config_from_environment_variables(self, monkeypatch):
        """
        GIVEN API_ID and API_HASH are set as environment variables
        WHEN calling load_config
        THEN returns config dict with values from environment
        """
        from telegram_getter.utils import load_config

        monkeypatch.setenv("API_ID", "99999")
        monkeypatch.setenv("API_HASH", "envhash123")

        config = load_config()

        assert config["api_id"] == "99999"
        assert config["api_hash"] == "envhash123"


class TestSanitizeFilename:
    """Test filename sanitization utility."""

    def test_sanitize_filename_removes_invalid_chars(self):
        """
        GIVEN a filename with invalid characters
        WHEN calling sanitize_filename
        THEN returns a safe filename
        """
        from telegram_getter.utils import sanitize_filename

        result = sanitize_filename("test/file:name*.txt")
        assert "/" not in result
        assert ":" not in result
        assert "*" not in result

    def test_sanitize_filename_preserves_valid_chars(self):
        """
        GIVEN a valid filename
        WHEN calling sanitize_filename
        THEN returns the same filename
        """
        from telegram_getter.utils import sanitize_filename

        result = sanitize_filename("valid_filename-123.txt")
        assert result == "valid_filename-123.txt"

    def test_sanitize_filename_handles_empty_string(self):
        """
        GIVEN an empty string
        WHEN calling sanitize_filename
        THEN returns a default filename
        """
        from telegram_getter.utils import sanitize_filename

        result = sanitize_filename("")
        assert len(result) > 0


class TestFormatSize:
    """Test human-readable size formatting."""

    def test_format_size_bytes(self):
        """
        GIVEN a size in bytes (< 1024)
        WHEN calling format_size
        THEN returns size with B suffix
        """
        from telegram_getter.utils import format_size

        assert format_size(512) == "512 B"
        assert format_size(0) == "0 B"

    def test_format_size_kilobytes(self):
        """
        GIVEN a size in kilobytes range
        WHEN calling format_size
        THEN returns size with KB suffix
        """
        from telegram_getter.utils import format_size

        result = format_size(1024)
        assert "KB" in result or "K" in result

    def test_format_size_megabytes(self):
        """
        GIVEN a size in megabytes range
        WHEN calling format_size
        THEN returns size with MB suffix
        """
        from telegram_getter.utils import format_size

        result = format_size(1024 * 1024)
        assert "MB" in result or "M" in result

    def test_format_size_gigabytes(self):
        """
        GIVEN a size in gigabytes range
        WHEN calling format_size
        THEN returns size with GB suffix
        """
        from telegram_getter.utils import format_size

        result = format_size(1024 * 1024 * 1024)
        assert "GB" in result or "G" in result
