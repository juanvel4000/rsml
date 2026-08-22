"""hmac-sha256 token generation for rsml"""

import hashlib
import hmac


def generate_token(secret: str | bytes, purpose: str, value: str) -> str:
    """generate a hmac token from a secret, purpose, and value"""
    secret = secret.encode() if isinstance(secret, str) else secret
    return hmac.new(
        secret, (purpose + ":" + value).encode(), hashlib.sha256
    ).hexdigest()
