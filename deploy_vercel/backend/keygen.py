"""
Cryptographic Key Generation and Validation Engine for Media Downloader Pro.
Handles license formatting, HMAC-SHA256 digital signing, and HWID fingerprinting.
"""

import os
import re
import sys
import hmac
import hashlib
import secrets
import string
import platform
import subprocess
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple

# Master Secret Key for cryptographic signatures
# (Can be overridden via environment variable MASTER_LICENSE_SECRET)
DEFAULT_MASTER_SECRET = "MDP-MASTER-SECRET-9f8a2b7c4d1e6f3a-PRO-2026"
MASTER_SECRET = os.environ.get("MASTER_LICENSE_SECRET", DEFAULT_MASTER_SECRET).encode("utf-8")

# License Key Prefixes & Plan Mapping
PLAN_CODES = {
    "pro_monthly": "MON",
    "pro_yearly": "YEA",
    "pro_lifetime": "LFT",
    "pro_custom": "CUS"
}

CODE_TO_PLAN = {v: k for k, v in PLAN_CODES.items()}


def generate_random_chunk(length: int = 4) -> str:
    """Generate uppercase alphanumeric random chunk."""
    chars = string.ascii_uppercase + string.digits
    # Remove easily confused characters: 0, O, 1, I
    chars = chars.replace('0', '').replace('O', '').replace('1', '').replace('I', '')
    return ''.join(secrets.choice(chars) for _ in range(length))


def generate_license_key(plan: str = "pro_yearly") -> str:
    """
    Generate cryptographically self-verifying license key.
    Format: MDP-{CODE}-{XXXX}-{XXXX}-{SIG}
    Example: MDP-LFT-72C8-DLMH-DD03
    """
    code = PLAN_CODES.get(plan, "PRO")
    c1 = generate_random_chunk(4)
    c2 = generate_random_chunk(4)
    data_to_sign = f"MDP-{code}-{c1}-{c2}"
    sig = hmac.new(MASTER_SECRET, data_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()[:4].upper()
    return f"{data_to_sign}-{sig}"


def verify_key_signature(key: str) -> Tuple[bool, Optional[str]]:
    """
    Verify if a license key contains a valid cryptographic HMAC signature.
    Returns: (is_valid: bool, plan_name: Optional[str])
    """
    formatted = format_license_key(key)
    parts = formatted.split('-')
    if len(parts) != 5 or parts[0] != "MDP":
        return False, None

    code, c1, c2, sig = parts[1], parts[2], parts[3], parts[4]
    data_to_sign = f"MDP-{code}-{c1}-{c2}"
    expected_sig = hmac.new(MASTER_SECRET, data_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()[:4].upper()

    if hmac.compare_digest(sig, expected_sig):
        plan = CODE_TO_PLAN.get(code, "pro_yearly")
        return True, plan
    return False, None


def format_license_key(raw_input: str) -> str:
    """Sanitize and format license key string."""
    if not raw_input:
        return ""
    raw = raw_input.strip().upper()
    # Check if already hyphen/space separated
    parts = [p for p in re.split(r'[-_\s]+', raw) if p]
    if parts and parts[0] == "MDP" and len(parts) >= 4:
        return "-".join(parts[:5])

    cleaned = re.sub(r'[^A-Za-z0-9]', '', raw)
    if cleaned.startswith("MDP"):
        cleaned = cleaned[3:]

    # Check for known 3/4 char plan code prefixes
    code = ""
    for c in ["MON", "YEA", "LFT", "PRO"]:
        if cleaned.startswith(c):
            code = c
            cleaned = cleaned[len(c):]
            break

    chunks = ["MDP"]
    if code:
        chunks.append(code)
    for i in range(0, len(cleaned), 4):
        chunk = cleaned[i:i+4]
        if chunk:
            chunks.append(chunk)
    return "-".join(chunks[:5])


_CACHED_HWID = None

def get_hardware_id() -> str:
    """
    Generate a stable, tamper-resistant Hardware Identifier (HWID)
    bound to the user's physical computer motherboard & CPU.
    Completely silent without console/CMD windows and cached in memory.
    """
    global _CACHED_HWID
    if _CACHED_HWID:
        return _CACHED_HWID

    identifiers = []

    # 1. Platform architecture & node
    identifiers.append(platform.machine())
    identifiers.append(platform.processor())

    # 2. Windows-specific hardware identifiers (WMIC / PowerShell / Registry)
    if sys.platform == 'win32':
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        creationflags = 0x08000000  # CREATE_NO_WINDOW

        # Bios / Motherboard Serial
        try:
            cmd = "Get-CimInstance Win32_BIOS | Select-Object -ExpandProperty SerialNumber"
            res = subprocess.check_output(
                ["powershell", "-NoProfile", "-NonInteractive", "-WindowStyle", "Hidden", "-Command", cmd],
                text=True,
                stderr=subprocess.DEVNULL,
                startupinfo=startupinfo,
                creationflags=creationflags,
                timeout=2.0
            )
            if res.strip():
                identifiers.append(res.strip())
        except Exception:
            pass

        # Motherboard UUID
        try:
            cmd = "Get-CimInstance Win32_ComputerSystemProduct | Select-Object -ExpandProperty UUID"
            res = subprocess.check_output(
                ["powershell", "-NoProfile", "-NonInteractive", "-WindowStyle", "Hidden", "-Command", cmd],
                text=True,
                stderr=subprocess.DEVNULL,
                startupinfo=startupinfo,
                creationflags=creationflags,
                timeout=2.0
            )
            if res.strip():
                identifiers.append(res.strip())
        except Exception:
            pass

        # Windows MachineGuid (Registry)
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography")
            guid, _ = winreg.QueryValueEx(key, "MachineGuid")
            winreg.CloseKey(key)
            if guid:
                identifiers.append(guid)
        except Exception:
            pass

    # Fallback to node name if empty
    if not identifiers:
        identifiers.append(platform.node())

    raw_string = "|".join(identifiers)
    hwid = hashlib.sha256(raw_string.encode('utf-8')).hexdigest()[:32].upper()
    _CACHED_HWID = f"HWID-{hwid[:4]}-{hwid[4:8]}-{hwid[8:12]}-{hwid[12:16]}"
    return _CACHED_HWID


def sign_license_payload(payload: Dict[str, Any]) -> str:
    """
    Generate HMAC-SHA256 cryptographic signature for a license payload dictionary.
    Guarantees tamper-proof local license validation with consistent boolean/integer normalization.
    """
    sorted_pairs = []
    for k in sorted(payload.keys()):
        if k != "signature":
            val = payload[k]
            if isinstance(val, bool):
                val = 1 if val else 0
            sorted_pairs.append(f"{k}={val}")
    data_str = "&".join(sorted_pairs)
    return hmac.new(MASTER_SECRET, data_str.encode('utf-8'), hashlib.sha256).hexdigest()


def verify_license_payload(payload: Dict[str, Any]) -> bool:
    """
    Verify the cryptographic signature and validity of a license payload.
    Supports both normalized boolean signatures and legacy signatures.
    """
    if not payload or not isinstance(payload, dict):
        return False
    expected_sig = payload.get("signature")
    if not expected_sig:
        return False

    computed_sig = sign_license_payload(payload)
    if hmac.compare_digest(expected_sig, computed_sig):
        return True

    # Fallback for legacy raw values
    raw_pairs = []
    for k in sorted(payload.keys()):
        if k != "signature":
            raw_pairs.append(f"{k}={payload[k]}")
    raw_sig = hmac.new(MASTER_SECRET, "&".join(raw_pairs).encode('utf-8'), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected_sig, raw_sig)


def calculate_expiry(plan: str, custom_days: Optional[int] = None) -> Optional[datetime]:
    """Calculate expiration datetime based on plan tier."""
    now = datetime.utcnow()
    if plan == "pro_monthly":
        return now + timedelta(days=30)
    elif plan == "pro_yearly":
        return now + timedelta(days=365)
    elif plan == "pro_lifetime":
        return None  # No expiration
    elif plan == "pro_custom" and custom_days:
        return now + timedelta(days=int(custom_days))
    return now + timedelta(days=30)
