"""
infra/security – Security infrastructure layer.

Exports:
  SecurityMiddleware           – ASGI middleware (Task 3.1)
  register_security_middleware – Registration helper
  limiter                      – slowapi Limiter singleton (Task 3.2)
  is_whitelisted               – Zero-arg whitelist predicate (Task 3.2)
  setup_rate_limiter           – Rate-limiter wiring helper (Task 3.2)
  EncryptedString              – SQLAlchemy TypeDecorator for AES-encrypted columns (Task 3.4)
  rotate_key                   – Single-value key-rotation helper (Task 3.4)
  EncryptionConfigError        – Raised when ENCRYPTION_KEY is absent/invalid (Task 3.4)
  DecryptionError              – Raised on ciphertext tampering/key mismatch (Task 3.4)
"""

from .encryption import (
    DecryptionError,
    EncryptedString,
    EncryptionConfigError,
    rotate_key,
)
from .middleware import SecurityMiddleware, register_security_middleware
from .rate_limit import is_whitelisted, limiter, setup_rate_limiter

__all__ = [
    "SecurityMiddleware",
    "register_security_middleware",
    "limiter",
    "is_whitelisted",
    "setup_rate_limiter",
    "EncryptedString",
    "rotate_key",
    "EncryptionConfigError",
    "DecryptionError",
]
