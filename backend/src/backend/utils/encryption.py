"""Fernet-based symmetric encryption utility for secrets stored at rest.

Feature 005: used to encrypt LLM provider API keys before persisting them
to the database, ensuring plaintext keys are never written to storage.

The encryption key is derived from the application ``SECRET_KEY`` using
PBKDF2-HMAC-SHA256 so that a compromised database row cannot be decrypted
without the application secret.

Example::

    encrypted = encrypt_secret("sk-anthropic-key", secret_key="my-app-secret")
    plaintext = decrypt_secret(encrypted, secret_key="my-app-secret")
    assert plaintext == "sk-anthropic-key"
"""

import base64
import os

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Salt used when deriving the Fernet key from SECRET_KEY.
# A fixed salt is acceptable here because the secret itself is unique per
# deployment; the salt prevents rainbow-table attacks on the derived key.
_PBKDF2_SALT = b"sms-researcher-v1"
_PBKDF2_ITERATIONS = 390_000  # OWASP 2023 recommended minimum for PBKDF2-SHA256


def _derive_fernet_key(secret_key: str) -> bytes:
    """Derive a 32-byte Fernet-compatible key from an application secret.

    Args:
        secret_key: The application secret key (from ``Settings.secret_key``).

    Returns:
        A URL-safe base64-encoded 32-byte key suitable for :class:`Fernet`.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=_PBKDF2_SALT,
        iterations=_PBKDF2_ITERATIONS,
    )
    raw = kdf.derive(secret_key.encode("utf-8"))
    return base64.urlsafe_b64encode(raw)


def encrypt_secret(plaintext: str, secret_key: str) -> bytes:
    """Encrypt a plaintext secret using Fernet symmetric encryption.

    The ciphertext is authenticated (HMAC-SHA256) so any tampering is
    detected during decryption.

    Args:
        plaintext: The secret string to encrypt (e.g. an API key).
        secret_key: The application secret key used to derive the Fernet key.

    Returns:
        Fernet-encrypted ciphertext as raw bytes suitable for storing in a
        ``LargeBinary`` database column.
    """
    key = _derive_fernet_key(secret_key)
    f = Fernet(key)
    return f.encrypt(plaintext.encode("utf-8"))


def decrypt_secret(ciphertext: bytes, secret_key: str) -> str:
    """Decrypt a Fernet-encrypted secret back to plaintext.

    Args:
        ciphertext: The encrypted bytes previously produced by
            :func:`encrypt_secret`.
        secret_key: The application secret key used to derive the Fernet key.
            Must be the same key used during encryption.

    Returns:
        The decrypted plaintext string.

    Raises:
        InvalidToken: If the ciphertext was tampered with, is malformed,
            or was encrypted with a different key.
    """
    key = _derive_fernet_key(secret_key)
    f = Fernet(key)
    return f.decrypt(ciphertext).decode("utf-8")


__all__ = ["encrypt_secret", "decrypt_secret", "InvalidToken"]
