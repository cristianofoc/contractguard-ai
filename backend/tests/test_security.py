"""
Unit tests for core utility functions: password hashing, JWT creation.
These tests do NOT require a database or external services.
"""

import pytest
from jose import jwt

from app.config import settings
from app.utils.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


class TestPasswordHashing:
    def test_hash_is_not_plain(self):
        hashed = hash_password("mysecretpassword")
        assert hashed != "mysecretpassword"

    def test_verify_correct_password(self):
        hashed = hash_password("correcthorse")
        assert verify_password("correcthorse", hashed) is True

    def test_verify_wrong_password(self):
        hashed = hash_password("correcthorse")
        assert verify_password("batterystaple", hashed) is False

    def test_different_hashes_for_same_password(self):
        """bcrypt salts ensure the same password produces different hashes."""
        h1 = hash_password("same")
        h2 = hash_password("same")
        assert h1 != h2


class TestJWT:
    def test_create_and_decode_token(self):
        import uuid

        user_id = uuid.uuid4()
        token = create_access_token({"sub": str(user_id)})
        payload = decode_access_token(token)
        assert payload["sub"] == str(user_id)

    def test_token_contains_exp(self):
        token = create_access_token({"sub": "test"})
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert "exp" in payload

    def test_invalid_token_raises(self):
        from jose import JWTError

        with pytest.raises(JWTError):
            decode_access_token("not.a.valid.token")
