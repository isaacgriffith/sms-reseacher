"""TOTP (Time-based One-Time Password) helpers.

Wraps ``pyotp`` for secret generation and code verification, and ``qrcode``
for QR image generation used in the 2FA setup flow.
"""

import base64
import io

import pyotp
import qrcode


def generate_secret() -> str:
    """Generate a random base32 TOTP secret.

    Returns:
        A random base32-encoded string suitable for use as a TOTP secret.
    """
    return pyotp.random_base32()


def get_provisioning_uri(secret: str, email: str, issuer: str) -> str:
    """Build an ``otpauth://`` provisioning URI for an authenticator app.

    Args:
        secret: The base32 TOTP secret.
        email: The account identifier shown in the authenticator app.
        issuer: The service/app name shown in the authenticator app.

    Returns:
        An ``otpauth://totp/`` URI string.
    """
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=email, issuer_name=issuer)


def generate_qr_base64(uri: str) -> str:
    """Encode a provisioning URI as a base64 PNG QR code image.

    Args:
        uri: An ``otpauth://`` URI as returned by :func:`get_provisioning_uri`.

    Returns:
        A base64-encoded PNG string suitable for use in an ``<img src>`` tag.
    """
    img = qrcode.make(uri)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


def verify_code(secret: str, code: str, valid_window: int = 1) -> bool:
    """Verify a TOTP code against a secret.

    Args:
        secret: The base32 TOTP secret.
        code: The 6-digit code supplied by the user.
        valid_window: Number of time-steps before and after the current step
            to accept (default ``1`` = ±30 seconds = 90 s total tolerance).

    Returns:
        ``True`` if the code is valid within the tolerance window.
    """
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=valid_window)
