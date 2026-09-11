import hmac
import hashlib

API_SECRET_KEY = b"quadruped_secure_token_2026"

def verify_token(payload: bytes, signature: str) -> bool:
    """Verifies HMAC-SHA256 signature for API / Socket commands."""
    expected_sig = hmac.new(API_SECRET_KEY, payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected_sig, signature)