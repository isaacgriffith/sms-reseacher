"""Fernet symmetric encryption helpers for sensitive stored values.

Used to encrypt TOTP secrets at rest.  The encryption key is derived from
``settings.secret_key`` via HKDF-SHA256 so no additional secret management
is required.
"""

import base64

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

from backend.core.config import get_settings

_HKDF_INFO = b"sms-researcher-totp-encryption-v1"
_HKDF_LENGTH = 32


def _derive_key() -> bytes:
    """Derive a 32-byte Fernet key from ``settings.secret_key`` via HKDF-SHA256.

    Returns:
        A URL-safe base64-encoded 32-byte key suitable for :class:`Fernet`.

    """
    settings = get_settings()
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=_HKDF_LENGTH,
        salt=None,
        info=_HKDF_INFO,
    )
    raw_key = hkdf.derive(settings.secret_key.encode())
    return base64.urlsafe_b64encode(raw_key)


def encrypt_secret(plaintext: str) -> str:
    """Encrypt *plaintext* with Fernet and return a base64-encoded ciphertext string.

    Args:
        plaintext: The sensitive value to encrypt (e.g. a TOTP secret).

    Returns:
        A URL-safe base64-encoded encrypted string suitable for database storage.

    """
    fernet = Fernet(_derive_key())
    return fernet.encrypt(plaintext.encode()).decode()


def decrypt_secret(ciphertext: str) -> str:
    """Decrypt a *ciphertext* string previously produced by :func:`encrypt_secret`.

    Args:
        ciphertext: The encrypted base64 string from the database.

    Returns:
        The original plaintext value.

    Raises:
        cryptography.fernet.InvalidToken: If the ciphertext is invalid or the
            key has changed since encryption.

    """
    fernet = Fernet(_derive_key())
    return fernet.decrypt(ciphertext.encode()).decode()
