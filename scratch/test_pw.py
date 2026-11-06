import os
import sys
import hashlib
import secrets
import sqlite3

def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    pw_hash = hashlib.pbkdf2_hmac("sha256", password.strip().encode("utf-8"), salt.encode("utf-8"), 100000).hex()
    return f"{salt}:{pw_hash}"

def verify_password(stored: str, provided: str) -> bool:
    try:
        salt, pw_hash = stored.strip().split(":", 1)
        test_hash = hashlib.pbkdf2_hmac("sha256", provided.strip().encode("utf-8"), salt.encode("utf-8"), 100000).hex()
        return secrets.compare_digest(pw_hash, test_hash)
    except Exception:
        return False

# Quick test
h = hash_password("admin2026!")
assert verify_password(h, "admin2026!")
assert not verify_password(h, "wrongpass")
print("Password hash & verify OK")
