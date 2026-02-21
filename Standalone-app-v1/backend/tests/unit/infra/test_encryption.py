"""
Unit tests for src/infra/security/encryption.py  (Task 3.4).

Strategy
--------
- All tests use an in-process Fernet key — no application Settings needed.
- We patch ``src.infra.security.encryption._get_fernet`` to inject a
  controlled key, so tests are fully isolated from .env / config.
- ``EncryptedString`` is exercised by calling its SQLAlchemy hook methods
  directly (no running database required).
- ``rotate_key`` is tested end-to-end with two distinct known keys.

Coverage
--------
  TestFernetFromHex        – _fernet_from_hex() validation
  TestEncryptedStringBind  – process_bind_param (encrypt path)
  TestEncryptedStringResult– process_result_value (decrypt path)
  TestEncryptedStringRound – encrypt → decrypt roundtrip
  TestRotateKey            – rotate_key() utility
  TestEncryptionErrors     – EncryptionConfigError, DecryptionError
"""

import base64
import os
from unittest.mock import MagicMock, patch

import pytest
from cryptography.fernet import Fernet

from src.infra.security.encryption import (
    EncryptedString,
    EncryptionConfigError,
    DecryptionError,
    _fernet_from_hex,
    rotate_key,
)


# ---------------------------------------------------------------------------
# Shared fixtures / helpers
# ---------------------------------------------------------------------------

def _random_key_hex() -> str:
    """Generate a valid 64-char hex key (32 bytes)."""
    return os.urandom(32).hex()


def _fernet_from_random() -> tuple[Fernet, str]:
    """Return (Fernet, key_hex) for a freshly generated key."""
    key_hex = _random_key_hex()
    fernet = _fernet_from_hex(key_hex)
    return fernet, key_hex


def _patch_fernet(fernet: Fernet):
    """Context manager: patch _get_fernet() to return *fernet*."""
    return patch("src.infra.security.encryption._get_fernet", return_value=fernet)


# ---------------------------------------------------------------------------
# 1. _fernet_from_hex
# ---------------------------------------------------------------------------

class TestFernetFromHex:
    """_fernet_from_hex() validates and constructs a Fernet from a hex key."""

    def test_valid_64_char_hex_returns_fernet(self):
        key_hex = _random_key_hex()
        f = _fernet_from_hex(key_hex)
        assert isinstance(f, Fernet)

    def test_fernet_is_functional(self):
        key_hex = _random_key_hex()
        f = _fernet_from_hex(key_hex)
        ct = f.encrypt(b"hello")
        assert f.decrypt(ct) == b"hello"

    def test_empty_string_raises_config_error(self):
        with pytest.raises(EncryptionConfigError, match="not configured"):
            _fernet_from_hex("")

    def test_non_hex_raises_config_error(self):
        with pytest.raises(EncryptionConfigError, match="not valid hexadecimal"):
            _fernet_from_hex("zz" * 32)

    def test_too_short_raises_config_error(self):
        short = "ab" * 16  # 16 bytes, not 32
        with pytest.raises(EncryptionConfigError, match="32 bytes"):
            _fernet_from_hex(short)

    def test_too_long_raises_config_error(self):
        long_hex = "ab" * 64  # 64 bytes, not 32
        with pytest.raises(EncryptionConfigError, match="32 bytes"):
            _fernet_from_hex(long_hex)

    def test_uppercase_hex_accepted(self):
        key_hex = _random_key_hex().upper()
        f = _fernet_from_hex(key_hex)
        assert isinstance(f, Fernet)


# ---------------------------------------------------------------------------
# 2. EncryptedString – process_bind_param (write path)
# ---------------------------------------------------------------------------

class TestEncryptedStringBind:
    """process_bind_param encrypts plaintext before DB write."""

    def _col(self) -> EncryptedString:
        return EncryptedString()

    def test_none_returns_none(self):
        col = self._col()
        fernet, _ = _fernet_from_random()
        with _patch_fernet(fernet):
            result = col.process_bind_param(None, dialect=MagicMock())
        assert result is None

    def test_string_is_encrypted(self):
        col = self._col()
        fernet, _ = _fernet_from_random()
        with _patch_fernet(fernet):
            result = col.process_bind_param("secret", dialect=MagicMock())
        assert result != "secret"
        assert isinstance(result, str)

    def test_result_is_valid_fernet_token(self):
        col = self._col()
        fernet, _ = _fernet_from_random()
        with _patch_fernet(fernet):
            result = col.process_bind_param("hello world", dialect=MagicMock())
        # Fernet tokens are URL-safe base64: should be decodable
        decoded = fernet.decrypt(result.encode())
        assert decoded == b"hello world"

    def test_empty_string_is_encrypted_not_stored_as_null(self):
        col = self._col()
        fernet, _ = _fernet_from_random()
        with _patch_fernet(fernet):
            result = col.process_bind_param("", dialect=MagicMock())
        assert result is not None
        assert isinstance(result, str)

    def test_unicode_text_encrypted(self):
        col = self._col()
        fernet, _ = _fernet_from_random()
        with _patch_fernet(fernet):
            result = col.process_bind_param("emoji 🔐 €uro", dialect=MagicMock())
        plaintext = fernet.decrypt(result.encode()).decode("utf-8")
        assert plaintext == "emoji 🔐 €uro"


# ---------------------------------------------------------------------------
# 3. EncryptedString – process_result_value (read path)
# ---------------------------------------------------------------------------

class TestEncryptedStringResult:
    """process_result_value decrypts ciphertext after DB read."""

    def _col(self) -> EncryptedString:
        return EncryptedString()

    def test_none_returns_none(self):
        col = self._col()
        fernet, _ = _fernet_from_random()
        with _patch_fernet(fernet):
            result = col.process_result_value(None, dialect=MagicMock())
        assert result is None

    def test_valid_ciphertext_decrypted(self):
        col = self._col()
        fernet, _ = _fernet_from_random()
        ciphertext = fernet.encrypt(b"plaintext").decode()
        with _patch_fernet(fernet):
            result = col.process_result_value(ciphertext, dialect=MagicMock())
        assert result == "plaintext"

    def test_tampered_ciphertext_raises_decryption_error(self):
        col = self._col()
        fernet, _ = _fernet_from_random()
        with _patch_fernet(fernet):
            with pytest.raises(DecryptionError, match="tampered"):
                col.process_result_value("notvalidfernet", dialect=MagicMock())

    def test_wrong_key_raises_decryption_error(self):
        col = self._col()
        fernet_a, _ = _fernet_from_random()
        fernet_b, _ = _fernet_from_random()
        # Encrypt with key A, try to decrypt with key B
        ciphertext = fernet_a.encrypt(b"secret").decode()
        with _patch_fernet(fernet_b):
            with pytest.raises(DecryptionError):
                col.process_result_value(ciphertext, dialect=MagicMock())


# ---------------------------------------------------------------------------
# 4. Encrypt → decrypt roundtrip
# ---------------------------------------------------------------------------

class TestEncryptedStringRound:
    """End-to-end: bind_param → result_value yields the original value."""

    def _round_trip(self, value):
        col = EncryptedString()
        fernet, _ = _fernet_from_random()
        dialect = MagicMock()
        with _patch_fernet(fernet):
            encrypted = col.process_bind_param(value, dialect=dialect)
            decrypted = col.process_result_value(encrypted, dialect=dialect)
        return decrypted

    def test_roundtrip_plain_text(self):
        assert self._round_trip("hello world") == "hello world"

    def test_roundtrip_none(self):
        assert self._round_trip(None) is None

    def test_roundtrip_empty_string(self):
        assert self._round_trip("") == ""

    def test_roundtrip_long_text(self):
        long_text = "x" * 10_000
        assert self._round_trip(long_text) == long_text

    def test_roundtrip_special_chars(self):
        text = "<script>alert(1)</script>\n\t"
        assert self._round_trip(text) == text

    def test_roundtrip_unicode(self):
        text = "日本語 🔐 €£"
        assert self._round_trip(text) == text

    def test_each_encryption_produces_different_ciphertext(self):
        """Fernet uses a random IV — same plaintext yields different ciphertext."""
        col = EncryptedString()
        fernet, _ = _fernet_from_random()
        dialect = MagicMock()
        with _patch_fernet(fernet):
            ct1 = col.process_bind_param("same", dialect=dialect)
            ct2 = col.process_bind_param("same", dialect=dialect)
        assert ct1 != ct2  # IVs differ — ciphertexts must differ


# ---------------------------------------------------------------------------
# 5. rotate_key
# ---------------------------------------------------------------------------

class TestRotateKey:
    """rotate_key() re-encrypts ciphertext from old key to new key."""

    def test_rotated_ciphertext_decryptable_with_new_key(self):
        old_hex = _random_key_hex()
        new_hex = _random_key_hex()
        old_fernet = _fernet_from_hex(old_hex)
        new_fernet = _fernet_from_hex(new_hex)

        original = "sensitive data"
        ciphertext = old_fernet.encrypt(original.encode()).decode()

        rotated = rotate_key(old_hex, new_hex, ciphertext)

        # New ciphertext must decrypt with new key
        assert new_fernet.decrypt(rotated.encode()).decode() == original

    def test_rotated_ciphertext_not_decryptable_with_old_key(self):
        from cryptography.fernet import InvalidToken

        old_hex = _random_key_hex()
        new_hex = _random_key_hex()
        old_fernet = _fernet_from_hex(old_hex)

        ciphertext = old_fernet.encrypt(b"data").decode()
        rotated = rotate_key(old_hex, new_hex, ciphertext)

        with pytest.raises(InvalidToken):
            old_fernet.decrypt(rotated.encode())

    def test_rotate_with_invalid_old_key_raises_config_error(self):
        with pytest.raises(EncryptionConfigError):
            rotate_key("nothex", _random_key_hex(), "someciphertext")

    def test_rotate_with_invalid_new_key_raises_config_error(self):
        old_hex = _random_key_hex()
        old_fernet = _fernet_from_hex(old_hex)
        ct = old_fernet.encrypt(b"data").decode()
        with pytest.raises(EncryptionConfigError):
            rotate_key(old_hex, "nothex", ct)

    def test_rotate_with_wrong_old_key_raises_decryption_error(self):
        correct_old_hex = _random_key_hex()
        wrong_old_hex = _random_key_hex()
        new_hex = _random_key_hex()

        fernet = _fernet_from_hex(correct_old_hex)
        ct = fernet.encrypt(b"data").decode()

        with pytest.raises(DecryptionError, match="rotate_key"):
            rotate_key(wrong_old_hex, new_hex, ct)

    def test_rotate_preserves_exact_plaintext(self):
        old_hex = _random_key_hex()
        new_hex = _random_key_hex()
        new_fernet = _fernet_from_hex(new_hex)
        old_fernet = _fernet_from_hex(old_hex)

        for plaintext in ["", "hello", "emoji 🔐", "x" * 5000]:
            ct = old_fernet.encrypt(plaintext.encode()).decode()
            rotated = rotate_key(old_hex, new_hex, ct)
            assert new_fernet.decrypt(rotated.encode()).decode() == plaintext


# ---------------------------------------------------------------------------
# 6. Error / edge-case coverage
# ---------------------------------------------------------------------------

class TestEncryptionErrors:
    """Verify error types and messages are correct."""

    def test_encryption_config_error_is_runtime_error(self):
        assert issubclass(EncryptionConfigError, RuntimeError)

    def test_decryption_error_is_runtime_error(self):
        assert issubclass(DecryptionError, RuntimeError)

    def test_missing_key_error_message_contains_openssl(self):
        with pytest.raises(EncryptionConfigError) as exc_info:
            _fernet_from_hex("")
        assert "openssl" in str(exc_info.value).lower()

    def test_wrong_length_key_error_message_mentions_32_bytes(self):
        with pytest.raises(EncryptionConfigError) as exc_info:
            _fernet_from_hex("ab" * 10)  # 10 bytes
        assert "32 bytes" in str(exc_info.value)

    def test_cache_ok_is_true(self):
        """EncryptedString.cache_ok must be True to avoid SQLAlchemy warnings."""
        assert EncryptedString.cache_ok is True

    def test_impl_is_string(self):
        """Underlying DB column type must be String (VARCHAR/TEXT)."""
        from sqlalchemy import String
        assert issubclass(EncryptedString.impl, String)
