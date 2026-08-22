"""hmac-sha256 token generation for rsml"""

import hashlib
import hmac


def generate_token(secret: str, purpose: str, value: str) -> str:
    """generate a hmac token from a secret, purpose, and value"""
    return hmac.new(
        secret.encode(), (purpose + ":" + value).encode(), hashlib.sha256
    ).hexdigest()
