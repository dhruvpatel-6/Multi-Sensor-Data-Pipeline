import pytest
import os
import json
import hmac
import hashlib

def test_canonical_schema_existence():
    """Verify schema v3.0.0-Truth file is present in repository."""
    schema_path = os.path.join("schema", "canonical_telemetry_v3.json")
    assert os.path.exists(schema_path) == True

def test_security_auth_verification():
    """Verify security guard authentication token logic."""
    from security_guard import verify_token
    payload = b"sensor_stream_command_data"
    secret = b"quadruped_secure_token_2026"
    sig = hmac.new(secret, payload, hashlib.sha256).hexdigest()
    assert verify_token(payload, sig) == True

def test_session_recording_file_integrity():
    """Verify quadruped session log artifact exists."""
    assert os.path.exists("quadruped_session_recording.jsonl") == True