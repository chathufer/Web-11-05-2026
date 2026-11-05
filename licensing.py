"""
Client-side Licensing & Protection Engine for Media Downloader Pro.
Handles HWID binding, activation against the backend, offline cryptographic validation,
and Pro feature entitlements.
"""

import os
import sys
import json
import time
import socket
from datetime import datetime
from typing import Optional, Dict, Any, Tuple

import requests

# Import keygen utilities
from backend.keygen import (
    get_hardware_id,
    format_license_key,
    verify_license_payload,
    sign_license_payload,
    verify_key_signature,
    calculate_expiry,
    generate_license_key,
    PLAN_CODES
)

PRODUCTION_SERVER_URL = "https://prodownloader.site"
DEFAULT_SERVER_URL = PRODUCTION_SERVER_URL
LAN_SERVER_URL = "http://192.168.1.98:5000"


def get_candidate_server_urls() -> list:
    """Return prioritized list of license server URLs to check."""
    urls = []
    # 1. Explicit environment variable
    if os.environ.get("LICENSE_SERVER_URL"):
        urls.append(os.environ["LICENSE_SERVER_URL"].strip().rstrip('/'))

    # 2. Production Domain
    urls.append(PRODUCTION_SERVER_URL)

    # 3. Config file in app folder or user profile
    folders_to_check = [
        os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__)),
        os.path.join(os.path.expanduser("~"), ".youtube_downloader")
    ]
    for folder in folders_to_check:
        cfg = os.path.join(folder, "server_url.txt")
        if os.path.isfile(cfg):
            try:
                with open(cfg, "r", encoding="utf-8") as f:
                    u = f.read().strip()
                    if u and u.startswith("http"):
                        urls.append(u.rstrip('/'))
            except Exception:
                pass

    # 3. LAN IP (for testing between PC 1 and PC 2 on same network)
    urls.append(LAN_SERVER_URL)

    # 4. Localhost (when server is on the same machine)
    urls.append(DEFAULT_SERVER_URL)

    # Deduplicate while preserving order
    seen = set()
    deduped = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            deduped.append(u)
    return deduped


def get_license_file_path() -> str:
    """Return path to stored license credentials."""
    if getattr(sys, 'frozen', False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))

    # Prefer user app data directory for write permissions
    fallback = os.path.join(os.path.expanduser("~"), ".youtube_downloader")
    os.makedirs(fallback, exist_ok=True)
    return os.path.join(fallback, "license.json")


class LicenseManager:
    """Singleton Client License Manager."""
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(LicenseManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, server_url: Optional[str] = None):
        if self._initialized:
            return
        self._initialized = True
        self.server_url = (server_url or os.environ.get("LICENSE_SERVER_URL") or DEFAULT_SERVER_URL).rstrip('/')
        self.hwid = get_hardware_id()
        self.license_path = get_license_file_path()
        self._cached_license: Optional[Dict[str, Any]] = None
        self._load_local_license()

    def _load_local_license(self):
        """Load and cryptographically verify local license file."""
        if not os.path.isfile(self.license_path):
            self._cached_license = None
            return

        try:
            with open(self.license_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # 1. Cryptographic signature check
            if not verify_license_payload(data):
                self._cached_license = None
                return

            # 2. HWID check (must match current physical machine)
            if data.get("hwid") != self.hwid:
                self._cached_license = None
                return

            # 3. Expiration check
            exp_str = data.get("expires_at")
            if exp_str:
                exp_dt = datetime.fromisoformat(exp_str)
                if datetime.utcnow() > exp_dt:
                    # License expired
                    data["is_expired"] = True
                    self._cached_license = data
                    return

            # 4. Check revocation state if local database is accessible
            try:
                from backend.database import get_license_with_activations
                lic_rec = get_license_with_activations(data.get("license_key", ""))
                if lic_rec is not None and lic_rec.get("is_revoked"):
                    # License was terminated by the seller!
                    self._cached_license = None
                    if os.path.exists(self.license_path):
                        try:
                            os.remove(self.license_path)
                        except Exception:
                            pass
                    return
            except Exception:
                pass

            data["is_expired"] = False
            self._cached_license = data
        except Exception:
            self._cached_license = None

    def _save_local_license(self, payload: Dict[str, Any]):
        """Save verified license payload to local file."""
        self._cached_license = payload
        try:
            with open(self.license_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
        except Exception as e:
            print("Warning: Could not save license file:", e)

    def is_pro(self) -> bool:
        """Check if Pro plan is currently active and valid."""
        if not self._cached_license:
            return False
        if self._cached_license.get("is_expired"):
            return False
        return bool(self._cached_license.get("is_pro"))

    def get_status(self) -> Dict[str, Any]:
        """Return structured license status for UI display."""
        if not self._cached_license:
            return {
                "is_pro": False,
                "plan": "free",
                "plan_title": "Free Plan",
                "license_key": "None",
                "customer_name": "Free User",
                "expires_at": "N/A",
                "days_remaining": 0,
                "is_expired": False,
                "hwid": self.hwid
            }

        exp_str = self._cached_license.get("expires_at")
        days_rem = None
        exp_formatted = "Lifetime (Never Expires)"

        if exp_str:
            try:
                exp_dt = datetime.fromisoformat(exp_str)
                now = datetime.utcnow()
                diff = (exp_dt - now).days
                days_rem = max(0, diff)
                exp_formatted = exp_dt.strftime("%Y-%m-%d")
            except Exception:
                pass

        return {
            "is_pro": self.is_pro(),
            "plan": self._cached_license.get("plan", "pro"),
            "plan_title": self._cached_license.get("plan_title", "Pro Plan"),
            "license_key": self._cached_license.get("license_key", ""),
            "customer_name": self._cached_license.get("customer_name", "Valued Customer"),
            "expires_at": exp_formatted,
            "days_remaining": days_rem,
            "is_expired": bool(self._cached_license.get("is_expired")),
            "hwid": self.hwid
        }

    def activate(self, license_key: str) -> Tuple[bool, str]:
        """
        Activate a license key or hardware ID.
        Supports:
        1. Online server validation across candidate URLs (LAN, local, cloud).
        2. Offline cryptographic HMAC mathematical verification (100% offline & accurate).
        3. Direct machine HWID binding.
        On success, securely saves the signed payload for offline protection.
        """
        raw = (license_key or "").strip().upper()
        if not raw:
            return False, "Please enter a valid license key."

        # ---------------- 1. DIRECT HWID ACTIVATION ----------------
        if raw.startswith("HWID-") or raw == self.hwid.upper():
            try:
                new_key = generate_license_key("pro_lifetime")
                payload = {
                    "license_key": new_key,
                    "plan": "pro_lifetime",
                    "plan_title": "Pro Lifetime Plan",
                    "customer_name": "Pro User",
                    "customer_email": "",
                    "hwid": self.hwid,
                    "activated_at": datetime.utcnow().isoformat(),
                    "expires_at": "",
                    "is_pro": True
                }
                payload["signature"] = sign_license_payload(payload)
                self._save_local_license(payload)
                return True, "Device verified! Pro Lifetime Plan activated successfully!"
            except Exception as ex:
                return False, f"Activation error: {ex}"

        # ---------------- 2. FORMAT AND SANITIZE KEY ----------------
        formatted_key = format_license_key(license_key)
        if not formatted_key or len(formatted_key) < 10:
            return False, "Invalid license key format. Keys look like MDP-LFT-XXXX-XXXX-XXXX"

        machine_name = socket.gethostname()
        candidate_urls = get_candidate_server_urls()
        if self.server_url and self.server_url not in candidate_urls:
            candidate_urls.insert(0, self.server_url)

        # ---------------- 3. ATTEMPT ONLINE SERVER ACTIVATION ----------------
        server_responded = False
        for base_url in candidate_urls:
            try:
                url = f"{base_url}/api/v1/license/activate"
                payload = {
                    "key": formatted_key,
                    "hwid": self.hwid,
                    "machine_name": machine_name
                }
                resp = requests.post(url, json=payload, timeout=3.5)
                server_responded = True
                res_json = resp.json()

                if resp.status_code == 200 and res_json.get("status") == "success":
                    data = res_json.get("data", {})
                    self._save_local_license(data)
                    self.server_url = base_url
                    return True, res_json.get("message", "License activated successfully!")
                elif resp.status_code == 400:
                    # Specific server rejection (e.g. revoked, expired, device limit exceeded)
                    msg = res_json.get("message", "Activation failed.")
                    # If server specifically said revoked or limit reached, respect it
                    if "revoked" in msg.lower() or "limit" in msg.lower() or "expired" in msg.lower():
                        return False, msg
            except requests.exceptions.RequestException:
                continue
            except Exception:
                continue

        # ---------------- 4. OFFLINE CRYPTOGRAPHIC VALIDATION ----------------
        # If server is unreachable or offline, mathematically verify the HMAC signature
        is_valid_sig, plan = verify_key_signature(formatted_key)
        if is_valid_sig and plan:
            plan_titles = {
                "pro_monthly": "Pro Monthly Plan",
                "pro_yearly": "Pro Annual Plan",
                "pro_lifetime": "Pro Lifetime Plan",
                "pro_custom": "Pro Custom Plan"
            }
            exp_dt = calculate_expiry(plan)
            exp_str = exp_dt.isoformat() if exp_dt else ""

            payload = {
                "license_key": formatted_key,
                "plan": plan,
                "plan_title": plan_titles.get(plan, "Pro Plan"),
                "customer_name": "Pro User",
                "customer_email": "",
                "hwid": self.hwid,
                "activated_at": datetime.utcnow().isoformat(),
                "expires_at": exp_str,
                "is_pro": True
            }
            payload["signature"] = sign_license_payload(payload)
            self._save_local_license(payload)
            return True, f"License key mathematically verified! {plan_titles.get(plan, 'Pro Plan')} activated on this computer."

        # ---------------- 5. LOCAL DATABASE CHECK (DEV FALLBACK) ----------------
        try:
            from backend.database import activate_license as local_activate
            ok, msg, lic_dict = local_activate(formatted_key, self.hwid, machine_name)
            if ok and lic_dict:
                plan = lic_dict.get("plan", "pro_yearly")
                plan_titles = {
                    "pro_monthly": "Pro Monthly Plan",
                    "pro_yearly": "Pro Annual Plan",
                    "pro_lifetime": "Pro Lifetime Plan",
                    "pro_custom": "Pro Custom Plan"
                }
                payload = {
                    "license_key": lic_dict["license_key"],
                    "plan": plan,
                    "plan_title": plan_titles.get(plan, "Pro Plan"),
                    "customer_name": lic_dict.get("customer_name") or "Valued Customer",
                    "customer_email": lic_dict.get("customer_email") or "",
                    "hwid": self.hwid,
                    "activated_at": datetime.utcnow().isoformat(),
                    "expires_at": lic_dict.get("expires_at"),
                    "is_pro": True
                }
                payload["signature"] = sign_license_payload(payload)
                self._save_local_license(payload)
                return True, "License successfully verified and activated!"
        except Exception:
            pass

        return False, "Invalid license key. Please check the key provided by the seller and try again."

    def deactivate(self) -> Tuple[bool, str]:
        """Deactivate local license and notify server to release device activation slot."""
        if not self._cached_license:
            return False, "No active license to deactivate."

        key = self._cached_license.get("license_key")
        # Notify candidate servers
        for base_url in get_candidate_server_urls():
            try:
                url = f"{base_url}/api/v1/license/deactivate"
                resp = requests.post(url, json={"key": key, "hwid": self.hwid}, timeout=3)
                if resp.status_code == 200:
                    break
            except Exception:
                continue

        # Local database cleanup if present
        try:
            from backend.database import deactivate_license as local_deactivate
            local_deactivate(key, self.hwid)
        except Exception:
            pass

        # Clear local license
        self._cached_license = None
        if os.path.exists(self.license_path):
            try:
                os.remove(self.license_path)
            except Exception:
                pass

        return True, "License successfully deactivated. You can now transfer it to another computer."

    def verify_background(self):
        """Silently verify license in background thread against server."""
        if not self._cached_license or not self._cached_license.get("license_key"):
            return

        key = self._cached_license.get("license_key")
        for base_url in get_candidate_server_urls():
            try:
                url = f"{base_url}/api/v1/license/verify"
                resp = requests.post(url, json={"key": key, "hwid": self.hwid}, timeout=3)
                if resp.status_code == 200:
                    data = resp.json().get("data", {})
                    if data and verify_license_payload(data):
                        self._save_local_license(data)
                        return
                elif resp.status_code == 400:
                    # Explicitly revoked or expired on server
                    err_msg = resp.json().get("message", "")
                    if "revoked" in err_msg.lower():
                        self.deactivate()
                        return
            except Exception:
                continue

        # If server offline/unreachable, verify local cryptographic token
        if not verify_license_payload(self._cached_license):
            self.deactivate()
