"""
Encryption at Rest for TickerTracker backend (Task 3.4).

Provides a SQLAlchemy ``TypeDecorator`` that transparently encrypts values
before they are persisted to the database and decrypts them on read.

Algorithm: Fernet symmetric encryption (AES-128-CBC + HMAC-SHA256), from the
``cryptography`` library.  Messages are authenticated, so tampering is detected
at decrypt time.

Usage in SQLAlchemy models
--------------------------
::

    from src.infra.security.encryption import EncryptedString

    class EstimateModel(Base):
        __tablename__ = "estimates"

        ai_reasoning: Mapped[Optional[str]] = mapped_column(
            EncryptedString(), nullable=True
        )

Key management
--------------
The encryption key is sourced from ``Settings.ENCRYPTION_KEY`` (a
``SecretStr``).  The raw value must be a **64-character hexadecimal string**
(32 bytes), which can be generated with::

    openssl rand -hex 32

Internally the 32 raw bytes are encoded to URL-safe base64 to form a valid
Fernet key.

Key rotation
------------
Use the ``rotate_key`` helper to re-encrypt a single ciphertext without
exposing the plaintext outside of memory::

    new_ct = rotate_key(
        old_key_hex="aabb...",   # 64 hex chars of the old key
        new_key_hex="ccdd...",   # 64 hex chars of the new key
        ciphertext="gAAA...",    # existing Fernet ciphertext from the DB
    )

For bulk rotation:

1. Set both ``ENCRYPTION_KEY`` (new) and ``OLD_ENCRYPTION_KEY`` (old) in the env.
2. Run a migration script that iterates over affected rows, calling
   ``rotate_key(old, new, row.field)`` and saving the result.
3. Remove ``OLD_ENCRYPTION_KEY`` from env once all rows are migrated.

Notes
-----
- ``None`` values are stored as SQL ``NULL`` and never encrypted/decrypted.
- An empty or missing ``ENCRYPTION_KEY`` raises ``EncryptionConfigError`` at
  the first encrypt/decrypt attempt, not at import time (fail-fast at runtime).
- Ciphertext is stored as a UTF-8 string in the database column.
"""

from __future__ import annotations

import base64

import structlog
from cryptography.fernet import Fernet, InvalidToken
from sqlalchemy import String
from sqlalchemy.engine import Dialect
from sqlalchemy.types import TypeDecorator

_logger = structlog.get_logger(__name__)


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class EncryptionConfigError(RuntimeError):
    """Raised when ENCRYPTION_KEY is missing or has the wrong format."""


class DecryptionError(RuntimeError):
    """Raised when ciphertext is invalid or has been tampered with."""


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _get_settings():
    """Lazy import to avoid circular dependencies at module load time."""
    from src.shared.infra.config import get_settings
    return get_settings()


def _fernet_from_hex(key_hex: str) -> Fernet:
    """
    Build a Fernet instance from a 64-character hex key.

    Args:
        key_hex: 64 hexadecimal characters (32 bytes of raw key material).

    Returns:
        Configured :class:`cryptography.fernet.Fernet` instance.

    Raises:
        EncryptionConfigError: If the hex string is absent, has the wrong
            length, or contains invalid hex characters.
    """
    if not key_hex:
        raise EncryptionConfigError(
            "ENCRYPTION_KEY is not configured. "
            "Generate one with: openssl rand -hex 32"
        )
    try:
        raw_bytes = bytes.fromhex(key_hex)
    except ValueError as exc:
        raise EncryptionConfigError(
            f"ENCRYPTION_KEY is not valid hexadecimal: {exc}"
        ) from exc

    if len(raw_bytes) != 32:
        raise EncryptionConfigError(
            f"ENCRYPTION_KEY must be exactly 32 bytes (64 hex chars); "
            f"got {len(raw_bytes)} bytes ({len(key_hex)} hex chars)"
        )

    # Fernet requires a 32-byte key encoded as URL-safe base64 (44 chars + "=")
    fernet_key = base64.urlsafe_b64encode(raw_bytes)
    return Fernet(fernet_key)


def _get_fernet() -> Fernet:
    """Return a Fernet built from the current application settings."""
    settings = _get_settings()
    key_hex = settings.ENCRYPTION_KEY.get_secret_value()
    return _fernet_from_hex(key_hex)


# ---------------------------------------------------------------------------
# TypeDecorator
# ---------------------------------------------------------------------------


class EncryptedString(TypeDecorator):
    """
    SQLAlchemy column type that stores encrypted text.

    Transparently encrypts on write and decrypts on read using Fernet symmetric
    encryption.  ``None`` values pass through unchanged (stored as SQL NULL).

    The encryption key is read lazily from ``Settings.ENCRYPTION_KEY`` at the
    first encrypt/decrypt call, so the TypeDecorator can be safely imported
    without a running application context.

    Example::

        class MyModel(Base):
            secret: Mapped[Optional[str]] = mapped_column(
                EncryptedString(), nullable=True
            )
    """

    impl = String
    cache_ok = True  # Fernet key comes from settings, not from this instance

    def process_bind_param(
        self, value: str | None, dialect: Dialect
    ) -> str | None:
        """Encrypt *value* before it is written to the database."""
        if value is None:
            return None
        fernet = _get_fernet()
        ciphertext: bytes = fernet.encrypt(value.encode("utf-8"))
        return ciphertext.decode("utf-8")

    def process_result_value(
        self, value: str | None, dialect: Dialect
    ) -> str | None:
        """Decrypt *value* after it is read from the database."""
        if value is None:
            return None
        fernet = _get_fernet()
        try:
            plaintext: bytes = fernet.decrypt(value.encode("utf-8"))
        except InvalidToken as exc:
            _logger.warning(
                "Failed to decrypt database value — possible key mismatch or "
                "data corruption.",
                exc_info=True,
            )
            raise DecryptionError(
                "Ciphertext is invalid or has been tampered with. "
                "Check ENCRYPTION_KEY and data integrity."
            ) from exc
        return plaintext.decode("utf-8")


# ---------------------------------------------------------------------------
# Key-rotation utility
# ---------------------------------------------------------------------------


def rotate_key(old_key_hex: str, new_key_hex: str, ciphertext: str) -> str:
    """
    Re-encrypt *ciphertext* from *old_key_hex* to *new_key_hex*.

    This is a **single-value** helper intended to be called from a migration
    script.  The plaintext is never written to disk; it only exists briefly in
    memory during the function call.

    Args:
        old_key_hex: 64-char hex string of the key used to produce *ciphertext*.
        new_key_hex: 64-char hex string of the replacement key.
        ciphertext:  Fernet ciphertext string as stored in the database.

    Returns:
        New Fernet ciphertext string encrypted with *new_key_hex*.

    Raises:
        EncryptionConfigError: If either key hex is invalid.
        DecryptionError: If the ciphertext cannot be decrypted with *old_key_hex*.

    Example::

        new_ct = rotate_key(
            old_key_hex="aabb..." * 8,
            new_key_hex="ccdd..." * 8,
            ciphertext=row.ai_reasoning,
        )
        row.ai_reasoning = new_ct
        session.commit()
    """
    old_fernet = _fernet_from_hex(old_key_hex)
    new_fernet = _fernet_from_hex(new_key_hex)

    try:
        plaintext_bytes = old_fernet.decrypt(ciphertext.encode("utf-8"))
    except InvalidToken as exc:
        raise DecryptionError(
            "rotate_key: cannot decrypt ciphertext with old_key_hex — "
            "check that old_key_hex matches the original encryption key."
        ) from exc

    new_ciphertext_bytes = new_fernet.encrypt(plaintext_bytes)
    return new_ciphertext_bytes.decode("utf-8")
