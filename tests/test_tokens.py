import hashlib
import hmac

from rsml.tokens import generate_token


def test_generate_token():
    secret = b"test-secret"
    purpose = "verify"
    value = "example@127.0.0.1"

    expected = hmac.new(secret, b"verify:example@127.0.0.1", hashlib.sha256).hexdigest()

    assert generate_token(secret, purpose, value) == expected


def test_generate_token_accepts_string_secret():
    secret = "test-secret"
    purpose = "verify"
    value = "example@127.0.0.1"

    expected = hmac.new(
        secret.encode(), b"verify:example@127.0.0.1", hashlib.sha256
    ).hexdigest()

    assert generate_token(secret, purpose, value) == expected


def test_generate_token_purpose_separation():
    secret = "test-secret"
    value = "example@127.0.0.1"

    verify = generate_token(secret, "verify", value)
    unsub = generate_token(secret, "unsub", value)

    assert verify != unsub


def test_generate_token_format():
    token = generate_token(b"test-secret", "verify", "example@127.0.0.1")

    assert len(token) == 64
    assert all(c in "0123456789abcdef" for c in token)
