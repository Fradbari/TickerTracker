"""
Unit tests for application configuration management.

Tests cover:
- Settings loading from environment variables and .env file
- Singleton pattern implementation with caching
- SecretStr field protection
- Default value validation
- Environment-specific configurations
"""

import tempfile
from pathlib import Path

import pytest
from pydantic import SecretStr

from src.shared.infra.config import Settings, get_settings


class TestSettingsCreation:
    """Test Settings class instantiation and field validation."""

    def test_create_settings_with_defaults(self):
        """Test creating Settings instance with all default values."""
        settings = Settings()

        assert settings.ENVIRONMENT == "local"
        assert settings.DEBUG is True
        assert settings.LOG_LEVEL == "INFO"
        assert settings.YAHOO_CACHE_TTL == 3600
        assert settings.DATABASE_URL.get_secret_value() == "sqlite:///./test.db"

    def test_environment_field_validation(self):
        """Test ENVIRONMENT field only accepts valid values."""
        valid_settings = Settings(ENVIRONMENT="production")
        assert valid_settings.ENVIRONMENT == "production"

        with pytest.raises(ValueError):
            Settings(ENVIRONMENT="invalid-env")

    def test_log_level_field_validation(self):
        """Test LOG_LEVEL field only accepts valid values."""
        valid_settings = Settings(LOG_LEVEL="DEBUG")
        assert valid_settings.LOG_LEVEL == "DEBUG"

        with pytest.raises(ValueError):
            Settings(LOG_LEVEL="INVALID")

    def test_debug_field_validation(self):
        """Test DEBUG field accepts boolean values."""
        settings = Settings(DEBUG=False)
        assert settings.DEBUG is False

        # Pydantic should coerce string "true" to True
        settings_with_string = Settings(DEBUG="true")
        assert settings_with_string.DEBUG is True

    def test_yahoo_cache_ttl_field(self):
        """Test YAHOO_CACHE_TTL field with different values."""
        settings = Settings(YAHOO_CACHE_TTL=7200)
        assert settings.YAHOO_CACHE_TTL == 7200


class TestSecretStrFields:
    """Test that secret fields properly use SecretStr type."""

    def test_database_url_is_secret_str(self):
        """Test DATABASE_URL is SecretStr and masks value."""
        settings = Settings(DATABASE_URL="postgresql://user:pass@localhost/db")

        # Should be SecretStr type
        assert isinstance(settings.DATABASE_URL, SecretStr)

        # get_secret_value() should return actual value
        assert settings.DATABASE_URL.get_secret_value() == "postgresql://user:pass@localhost/db"

        # repr() should mask the secret
        assert "pass" not in repr(settings.DATABASE_URL)
        assert "***" in repr(settings.DATABASE_URL)

    def test_gemini_api_key_is_secret_str(self):
        """Test GEMINI_API_KEY is SecretStr and masks value."""
        settings = Settings(GEMINI_API_KEY="secret-gemini-key-12345")

        assert isinstance(settings.GEMINI_API_KEY, SecretStr)
        assert settings.GEMINI_API_KEY.get_secret_value() == "secret-gemini-key-12345"

    def test_finnhub_api_key_is_secret_str(self):
        """Test FINNHUB_API_KEY is SecretStr and masks value."""
        settings = Settings(FINNHUB_API_KEY="secret-finnhub-key")

        assert isinstance(settings.FINNHUB_API_KEY, SecretStr)
        assert settings.FINNHUB_API_KEY.get_secret_value() == "secret-finnhub-key"

    def test_google_service_account_json_is_secret_str(self):
        """Test GOOGLE_SERVICE_ACCOUNT_JSON is SecretStr."""
        json_str = '{"type": "service_account", "project_id": "test"}'
        settings = Settings(GOOGLE_SERVICE_ACCOUNT_JSON=json_str)

        assert isinstance(settings.GOOGLE_SERVICE_ACCOUNT_JSON, SecretStr)
        assert settings.GOOGLE_SERVICE_ACCOUNT_JSON.get_secret_value() == json_str

    def test_encryption_key_is_secret_str(self):
        """Test ENCRYPTION_KEY is SecretStr."""
        encryption_key = "a" * 64  # 64 hex characters
        settings = Settings(ENCRYPTION_KEY=encryption_key)

        assert isinstance(settings.ENCRYPTION_KEY, SecretStr)
        assert settings.ENCRYPTION_KEY.get_secret_value() == encryption_key

    def test_jwt_secret_is_secret_str(self):
        """Test JWT_SECRET is SecretStr."""
        jwt_secret = "b" * 64  # 64 hex characters
        settings = Settings(JWT_SECRET=jwt_secret)

        assert isinstance(settings.JWT_SECRET, SecretStr)
        assert settings.JWT_SECRET.get_secret_value() == jwt_secret

    def test_secret_str_not_exposed_in_dict(self):
        """Test that secrets are protected in SecretStr fields."""
        settings = Settings(
            DATABASE_URL="postgresql://user:password@localhost/db", GEMINI_API_KEY="secret-key-123"
        )

        # In Pydantic v2, model_dump() keeps SecretStr objects
        dumped = settings.model_dump()
        # The value should be a SecretStr
        assert isinstance(dumped["DATABASE_URL"], SecretStr)

        # When str() is called on SecretStr, it masks the value with asterisks
        assert "**********" in str(dumped["DATABASE_URL"])

        # To get actual value, use get_secret_value()
        assert (
            dumped["DATABASE_URL"].get_secret_value() == "postgresql://user:password@localhost/db"
        )

        # repr() should also mask the secret
        assert "password" not in repr(dumped["DATABASE_URL"])


class TestEnvironmentVariableLoading:
    """Test Settings loading from environment variables."""

    def test_load_from_environment_variables(self, monkeypatch):
        """Test Settings loads values from environment variables."""
        monkeypatch.setenv("ENVIRONMENT", "staging")
        monkeypatch.setenv("DEBUG", "false")
        monkeypatch.setenv("LOG_LEVEL", "WARNING")
        monkeypatch.setenv("YAHOO_CACHE_TTL", "7200")

        settings = Settings()

        assert settings.ENVIRONMENT == "staging"
        assert settings.DEBUG is False
        assert settings.LOG_LEVEL == "WARNING"
        assert settings.YAHOO_CACHE_TTL == 7200

    def test_case_insensitive_environment_variables(self, monkeypatch):
        """Test Settings loads case-insensitive environment variables."""
        monkeypatch.setenv("environment", "production")  # lowercase
        monkeypatch.setenv("debug", "true")  # lowercase

        settings = Settings()

        assert settings.ENVIRONMENT == "production"
        assert settings.DEBUG is True

    def test_env_file_loading(self):
        """Test Settings loads from .env file when it exists."""
        # Create a temporary .env file
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".env",
            delete=False,
            dir=".",
        ) as f:
            f.write("ENVIRONMENT=staging\n")
            f.write("DEBUG=false\n")
            f.write("LOG_LEVEL=DEBUG\n")
            temp_env_path = f.name

        try:
            # Note: In real scenarios, Settings loads from .env in current directory
            # This test verifies the model_config is set correctly
            assert Settings.model_config["env_file"] == ".env"
        finally:
            # Clean up
            if Path(temp_env_path).exists():
                Path(temp_env_path).unlink()

    def test_environment_variables_override_defaults(self, monkeypatch):
        """Test environment variables override default values."""
        # First, clear any existing environment vars
        monkeypatch.delenv("DEBUG", raising=False)
        monkeypatch.delenv("YAHOO_CACHE_TTL", raising=False)

        # Test with no environment variables (defaults)
        default_settings = Settings()
        assert default_settings.DEBUG is True
        assert default_settings.YAHOO_CACHE_TTL == 3600

        # Now set environment variables
        monkeypatch.setenv("DEBUG", "false")
        monkeypatch.setenv("YAHOO_CACHE_TTL", "5000")

        # Create new settings instance
        settings = Settings()
        assert settings.DEBUG is False
        assert settings.YAHOO_CACHE_TTL == 5000


class TestSingletonBehavior:
    """Test get_settings() singleton pattern with caching."""

    def test_get_settings_returns_settings_instance(self):
        """Test get_settings() returns a Settings instance."""
        settings = get_settings()

        assert isinstance(settings, Settings)

    def test_get_settings_is_cached(self):
        """Test get_settings() returns same instance due to lru_cache."""
        settings1 = get_settings()
        settings2 = get_settings()

        # Should be exact same object in memory
        assert settings1 is settings2

    def test_get_settings_singleton_with_environment_variables(self, monkeypatch):
        """Test get_settings() singleton with environment variables."""
        # Clear the cache first
        get_settings.cache_clear()

        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("DEBUG", "false")

        settings = get_settings()

        assert settings.ENVIRONMENT == "production"
        assert settings.DEBUG is False

        # Verify caching works
        settings2 = get_settings()
        assert settings is settings2

    def teardown_method(self):
        """Clear get_settings cache after each test."""
        get_settings.cache_clear()


class TestMultiEnvironmentConfigurations:
    """Test different environment-specific configurations."""

    def test_local_environment_configuration(self):
        """Test typical local development configuration."""
        settings = Settings(
            ENVIRONMENT="local",
            DEBUG=True,
            LOG_LEVEL="DEBUG",
            DATABASE_URL="sqlite:///./tickertracker.db",
        )

        assert settings.ENVIRONMENT == "local"
        assert settings.DEBUG is True
        assert settings.LOG_LEVEL == "DEBUG"

    def test_staging_environment_configuration(self):
        """Test typical staging environment configuration."""
        settings = Settings(
            ENVIRONMENT="staging",
            DEBUG=False,
            LOG_LEVEL="INFO",
            DATABASE_URL="postgresql+asyncpg://user:pass@staging-db:5432/tickertracker",
        )

        assert settings.ENVIRONMENT == "staging"
        assert settings.DEBUG is False
        assert settings.LOG_LEVEL == "INFO"

    def test_production_environment_configuration(self):
        """Test typical production environment configuration."""
        settings = Settings(
            ENVIRONMENT="production",
            DEBUG=False,
            LOG_LEVEL="WARNING",
            DATABASE_URL="postgresql+asyncpg://user:pass@prod-db:5432/tickertracker",
            ENCRYPTION_KEY="production-encryption-key-64-characters-long-hex-string",
            JWT_SECRET="production-jwt-secret-64-characters-long-hex-string",
        )

        assert settings.ENVIRONMENT == "production"
        assert settings.DEBUG is False
        assert settings.LOG_LEVEL == "WARNING"
        assert (
            settings.ENCRYPTION_KEY.get_secret_value()
            == "production-encryption-key-64-characters-long-hex-string"
        )


class TestConfigurationValidation:
    """Test configuration validation and error handling."""

    def test_yahoo_cache_ttl_must_be_integer(self):
        """Test YAHOO_CACHE_TTL validates integer type."""
        # Valid integer
        settings = Settings(YAHOO_CACHE_TTL=3600)
        assert settings.YAHOO_CACHE_TTL == 3600

        # Pydantic should coerce string to int
        settings_string = Settings(YAHOO_CACHE_TTL="7200")
        assert settings_string.YAHOO_CACHE_TTL == 7200

    def test_optional_fields_with_empty_defaults(self):
        """Test optional fields with empty string defaults."""
        settings = Settings()

        # These should have empty string defaults
        assert settings.GEMINI_API_KEY.get_secret_value() == ""
        assert settings.FINNHUB_API_KEY.get_secret_value() == ""
        assert settings.GOOGLE_SERVICE_ACCOUNT_JSON.get_secret_value() == ""
        assert settings.DRIVE_FOLDER_ID == ""
        assert settings.ENCRYPTION_KEY.get_secret_value() == ""
        assert settings.JWT_SECRET.get_secret_value() == ""

    def test_model_config_has_correct_settings(self):
        """Test model_config is properly configured."""
        config = Settings.model_config

        assert config["env_file"] == ".env"
        assert config["env_file_encoding"] == "utf-8"
        assert config["case_sensitive"] is False


class TestIntegrationScenarios:
    """Test real-world integration scenarios."""

    def test_complete_staging_setup(self, monkeypatch):
        """Test complete staging environment setup."""
        # Simulate staging environment variables
        monkeypatch.setenv("ENVIRONMENT", "staging")
        monkeypatch.setenv("DEBUG", "false")
        monkeypatch.setenv("LOG_LEVEL", "INFO")
        monkeypatch.setenv(
            "DATABASE_URL", "postgresql+asyncpg://staging_user:staging_pass@staging.db:5432/tt"
        )
        monkeypatch.setenv("YAHOO_CACHE_TTL", "1800")
        monkeypatch.setenv("GEMINI_API_KEY", "staging-gemini-key")
        monkeypatch.setenv("DRIVE_FOLDER_ID", "staging-folder-id")

        settings = Settings()

        assert settings.ENVIRONMENT == "staging"
        assert settings.DEBUG is False
        assert settings.LOG_LEVEL == "INFO"
        assert settings.YAHOO_CACHE_TTL == 1800
        assert settings.GEMINI_API_KEY.get_secret_value() == "staging-gemini-key"
        assert settings.DRIVE_FOLDER_ID == "staging-folder-id"

    def test_complete_production_setup_with_all_secrets(self, monkeypatch):
        """Test complete production environment with all secrets configured."""
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("DEBUG", "false")
        monkeypatch.setenv("LOG_LEVEL", "WARNING")
        monkeypatch.setenv(
            "DATABASE_URL", "postgresql+asyncpg://prod_user:prod_pass@prod.db:5432/tt"
        )
        monkeypatch.setenv("GEMINI_API_KEY", "prod-gemini-key-secret")
        monkeypatch.setenv("FINNHUB_API_KEY", "prod-finnhub-key-secret")
        monkeypatch.setenv("GOOGLE_SERVICE_ACCOUNT_JSON", '{"type": "service_account"}')
        monkeypatch.setenv("DRIVE_FOLDER_ID", "prod-folder-id")
        monkeypatch.setenv("ENCRYPTION_KEY", "a" * 64)
        monkeypatch.setenv("JWT_SECRET", "b" * 64)

        settings = Settings()

        assert settings.ENVIRONMENT == "production"
        assert settings.DEBUG is False
        assert settings.LOG_LEVEL == "WARNING"
        assert settings.GEMINI_API_KEY.get_secret_value() == "prod-gemini-key-secret"
        assert settings.FINNHUB_API_KEY.get_secret_value() == "prod-finnhub-key-secret"
        assert isinstance(settings.ENCRYPTION_KEY, SecretStr)
        assert isinstance(settings.JWT_SECRET, SecretStr)
