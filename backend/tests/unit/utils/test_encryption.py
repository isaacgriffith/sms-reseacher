"""Unit tests for backend.utils.encryption — T066.

Covers:
- encrypt → decrypt round-trip with correct key.
- Decryption with wrong key raises InvalidToken.
- Byte-stability: two calls to encrypt_secret produce different ciphertexts
  (Fernet uses random IV per call) but both decrypt correctly.
- Empty string encryption/decryption.
- Long string encryption/decryption.
"""

from __future__ import annotations

import pytest

from backend.utils.encryption import InvalidToken, decrypt_secret, encrypt_secret


class TestEncryptDecryptRoundTrip:
    """encrypt_secret + decrypt_secret round-trip tests."""

    def test_basic_roundtrip(self) -> None:
        """encrypt then decrypt returns the original plaintext."""
        plaintext = "sk-anthropic-test-key-abc123"
        secret = "my-super-secret-key"

        ciphertext = encrypt_secret(plaintext, secret)
        result = decrypt_secret(ciphertext, secret)

        assert result == plaintext

    def test_empty_string_roundtrip(self) -> None:
        """encrypt then decrypt works for empty string input."""
        plaintext = ""
        secret = "any-key"

        ciphertext = encrypt_secret(plaintext, secret)
        result = decrypt_secret(ciphertext, secret)

        assert result == plaintext

    def test_long_string_roundtrip(self) -> None:
        """encrypt then decrypt works for a long API key string."""
        plaintext = "sk-" + "a" * 500
        secret = "long-key-test"

        ciphertext = encrypt_secret(plaintext, secret)
        result = decrypt_secret(ciphertext, secret)

        assert result == plaintext

    def test_special_characters_roundtrip(self) -> None:
        """encrypt then decrypt preserves special characters."""
        plaintext = "sk-abc/def+XYZ=123!@#$%^&*()"
        secret = "special-char-test"

        ciphertext = encrypt_secret(plaintext, secret)
        result = decrypt_secret(ciphertext, secret)

        assert result == plaintext


class TestWrongKeyRaisesInvalidToken:
    """Decryption with the wrong key raises InvalidToken."""

    def test_wrong_key_raises_invalid_token(self) -> None:
        """decrypt_secret raises InvalidToken when using the wrong key."""
        plaintext = "secret-api-key"
        correct_key = "correct-secret"
        wrong_key = "wrong-secret"

        ciphertext = encrypt_secret(plaintext, correct_key)

        with pytest.raises(InvalidToken):
            decrypt_secret(ciphertext, wrong_key)

    def test_empty_wrong_key_raises_invalid_token(self) -> None:
        """decrypt_secret raises InvalidToken for empty wrong key."""
        plaintext = "secret"
        correct_key = "correct"
        wrong_key = "not-correct"

        ciphertext = encrypt_secret(plaintext, correct_key)

        with pytest.raises(InvalidToken):
            decrypt_secret(ciphertext, wrong_key)


class TestByteStability:
    """Fernet produces different ciphertexts per call (random IV) but both decrypt."""

    def test_two_encryptions_produce_different_ciphertexts(self) -> None:
        """Two calls to encrypt_secret with same input produce different bytes."""
        plaintext = "same-secret"
        secret = "same-key"

        ct1 = encrypt_secret(plaintext, secret)
        ct2 = encrypt_secret(plaintext, secret)

        # Fernet uses random IV so ciphertexts differ
        assert ct1 != ct2

    def test_both_ciphertexts_decrypt_correctly(self) -> None:
        """Both ciphertexts produced by encrypt_secret decrypt to the same plaintext."""
        plaintext = "same-secret"
        secret = "same-key"

        ct1 = encrypt_secret(plaintext, secret)
        ct2 = encrypt_secret(plaintext, secret)

        assert decrypt_secret(ct1, secret) == plaintext
        assert decrypt_secret(ct2, secret) == plaintext

    def test_ciphertext_is_bytes(self) -> None:
        """encrypt_secret returns bytes (not str)."""
        result = encrypt_secret("test", "key")
        assert isinstance(result, bytes)

    def test_tampered_ciphertext_raises_invalid_token(self) -> None:
        """Modifying the ciphertext causes InvalidToken during decryption."""
        plaintext = "original"
        secret = "key"

        ciphertext = encrypt_secret(plaintext, secret)
        # Flip a byte in the middle of the ciphertext
        tampered = bytearray(ciphertext)
        tampered[len(tampered) // 2] ^= 0xFF
        tampered_bytes = bytes(tampered)

        with pytest.raises(InvalidToken):
            decrypt_secret(tampered_bytes, secret)
