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
from datetime import datetime, timedelta
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



def _get_system_trial_marker_path() -> str:
    """Return machine-wide persistent storage path that survives user profile resets and app uninstallation."""
    program_data = os.environ.get("ALLUSERSPROFILE") or os.environ.get("ProgramData") or r"C:\ProgramData"
    folder = os.path.join(program_data, "MediaDownloaderPro")
    try:
        os.makedirs(folder, exist_ok=True)
    except Exception:
        pass
    return os.path.join(folder, "sys_fingerprint.dat")


def _get_trial_record_path() -> str:
    folder = os.path.join(os.path.expanduser("~"), ".youtube_downloader")
    try:
        os.makedirs(folder, exist_ok=True)
    except Exception:
        pass
    return os.path.join(folder, "trial_record.dat")


def record_trial_claim(hwid: str, started_at: str, expires_at: str, watermark: Optional[str] = None):
    """
    Multi-Tier Permanent Machine Trial Lock:
    Permanently writes the trial claim across 4 independent persistence layers:
    1. Machine-Wide System Directory (ProgramData) - Survives uninstallation and user profile switches.
    2. Windows Registry Primary Key (HKCU\Software\MediaDownloaderPro).
    3. Windows Registry Secondary Stealth Key (HKCU\Software\AppDataSystem\MDP_Core).
    4. Local User AppData Directory (~/.youtube_downloader/trial_record.dat).
    """
    clean_hwid = (hwid or "").strip().upper()
    now_str = datetime.utcnow().isoformat()
    clock_mark = watermark or now_str

    payload = {
        "hwid": clean_hwid,
        "trial_started_at": started_at,
        "trial_expires_at": expires_at,
        "clock_watermark": clock_mark,
        "claimed": 1
    }
    payload["sig"] = sign_license_payload(payload)

    # Layer 1: Machine-Wide System Storage (ProgramData)
    try:
        sys_path = _get_system_trial_marker_path()
        with open(sys_path, "w", encoding="utf-8") as f:
            json.dump(payload, f)
    except Exception:
        pass

    # Layer 2 & 3: Windows Registry (Primary + Secondary Stealth Key)
    if sys.platform == "win32":
        try:
            import winreg
            # Primary Key
            reg_key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\MediaDownloaderPro")
            winreg.SetValueEx(reg_key, "TrialClaimed", 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(reg_key, "TrialHWID", 0, winreg.REG_SZ, clean_hwid)
            winreg.SetValueEx(reg_key, "TrialStarted", 0, winreg.REG_SZ, started_at)
            winreg.SetValueEx(reg_key, "TrialExpires", 0, winreg.REG_SZ, expires_at)
            winreg.SetValueEx(reg_key, "ClockWatermark", 0, winreg.REG_SZ, clock_mark)
            winreg.CloseKey(reg_key)

            # Secondary Stealth Key
            stealth_key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\AppDataSystem\MDP_Core")
            winreg.SetValueEx(stealth_key, "Claimed", 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(stealth_key, "HWID", 0, winreg.REG_SZ, clean_hwid)
            winreg.SetValueEx(stealth_key, "Expires", 0, winreg.REG_SZ, expires_at)
            winreg.SetValueEx(stealth_key, "Watermark", 0, winreg.REG_SZ, clock_mark)
            winreg.CloseKey(stealth_key)
        except Exception:
            pass

    # Layer 4: Local User AppData Directory
    try:
        path = _get_trial_record_path()
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f)
    except Exception:
        pass


def check_trial_claimed(hwid: str) -> Tuple[bool, Optional[str], bool, str]:
    """
    Check if this physical machine (HWID) has ever claimed the 7-day trial across all 4 persistence layers.
    Includes Clock Rollback / Anti-Tampering Protection.
    Returns: (has_claimed: bool, expires_at: Optional[str], is_expired: bool, reason: str)
    """
    clean_hwid = (hwid or "").strip().upper()
    now_dt = datetime.utcnow()

    claimed = False
    earliest_started = None
    target_expires = None
    max_watermark = None

    def update_record(h, start_str, exp_str, mark_str):
        nonlocal claimed, earliest_started, target_expires, max_watermark
        if not h or h.strip().upper() == clean_hwid:
            claimed = True
            if exp_str and (not target_expires or exp_str < target_expires):
                target_expires = exp_str
            if start_str and (not earliest_started or start_str < earliest_started):
                earliest_started = start_str
            if mark_str and (not max_watermark or mark_str > max_watermark):
                max_watermark = mark_str

    # 1. Check Machine-Wide ProgramData Storage
    try:
        sys_path = _get_system_trial_marker_path()
        if os.path.isfile(sys_path):
            with open(sys_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if data.get("claimed") == 1:
                update_record(data.get("hwid"), data.get("trial_started_at"), data.get("trial_expires_at"), data.get("clock_watermark"))
    except Exception:
        pass

    # 2. Check Windows Registry Primary Key
    if sys.platform == "win32":
        try:
            import winreg
            reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\MediaDownloaderPro")
            c_val, _ = winreg.QueryValueEx(reg_key, "TrialClaimed")
            h_val, _ = winreg.QueryValueEx(reg_key, "TrialHWID")
            e_val, _ = winreg.QueryValueEx(reg_key, "TrialExpires")
            try:
                s_val, _ = winreg.QueryValueEx(reg_key, "TrialStarted")
            except Exception:
                s_val = None
            try:
                w_val, _ = winreg.QueryValueEx(reg_key, "ClockWatermark")
            except Exception:
                w_val = None
            winreg.CloseKey(reg_key)
            if c_val == 1:
                update_record(h_val, s_val, e_val, w_val)
        except Exception:
            pass

        # 3. Check Windows Registry Secondary Stealth Key
        try:
            import winreg
            stealth_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\AppDataSystem\MDP_Core")
            sc_val, _ = winreg.QueryValueEx(stealth_key, "Claimed")
            sh_val, _ = winreg.QueryValueEx(stealth_key, "HWID")
            se_val, _ = winreg.QueryValueEx(stealth_key, "Expires")
            try:
                sw_val, _ = winreg.QueryValueEx(stealth_key, "Watermark")
            except Exception:
                sw_val = None
            winreg.CloseKey(stealth_key)
            if sc_val == 1:
                update_record(sh_val, None, se_val, sw_val)
        except Exception:
            pass

    # 4. Check Local AppData File
    try:
        path = _get_trial_record_path()
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if data.get("claimed") == 1:
                update_record(data.get("hwid"), data.get("trial_started_at"), data.get("trial_expires_at"), data.get("clock_watermark"))
    except Exception:
        pass

    if not claimed:
        return False, None, False, "No trial claimed"

    # Anti-Clock-Tampering (Clock Rollback Check)
    clock_tampered = False
    if max_watermark:
        try:
            watermark_dt = datetime.fromisoformat(max_watermark)
            if now_dt < watermark_dt - timedelta(hours=1):
                clock_tampered = True
        except Exception:
            pass

    # Check natural expiration
    is_expired = False
    if target_expires:
        try:
            exp_dt = datetime.fromisoformat(target_expires)
            if now_dt >= exp_dt:
                is_expired = True
        except Exception:
            pass

    if clock_tampered:
        is_expired = True

    # Advance clock watermark to current system time if legitimate
    new_mark = now_dt.isoformat()
    if max_watermark and max_watermark > new_mark and not clock_tampered:
        new_mark = max_watermark

    # Self-Healing Synchronization: restore trial record to ALL 4 layers
    if earliest_started or target_expires:
        s_date = earliest_started or (datetime.fromisoformat(target_expires) - timedelta(days=7)).isoformat()
        e_date = target_expires or (datetime.fromisoformat(s_date) + timedelta(days=7)).isoformat()
        record_trial_claim(clean_hwid, s_date, e_date, watermark=new_mark)

    reason = "Clock tampering detected" if clock_tampered else ("Trial expired" if is_expired else "Trial active")
    return True, target_expires, is_expired, reason

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
            claimed, trial_exp, is_exp, _ = check_trial_claimed(self.hwid)
            if claimed and trial_exp and not is_exp:
                try:
                    machine_name = socket.gethostname()
                    trial_key = generate_license_key("pro_trial")
                    payload = {
                        "license_key": trial_key,
                        "plan": "pro_trial",
                        "plan_title": "Pro 7-Day Trial",
                        "customer_name": f"Trial User ({machine_name})",
                        "customer_email": "",
                        "hwid": self.hwid,
                        "activated_at": datetime.utcnow().isoformat(),
                        "expires_at": trial_exp,
                        "is_pro": True,
                        "is_trial": True,
                        "is_expired": False
                    }
                    payload["signature"] = sign_license_payload(payload)
                    self._save_local_license(payload)
                    return
                except Exception:
                    pass
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

            # 3. Expiration check & Trial lockdown check
            if data.get("plan") == "pro_trial":
                claimed, trial_exp, is_exp, _ = check_trial_claimed(self.hwid)
                if is_exp:
                    data["is_expired"] = True
                    data["is_pro"] = False
                    self._cached_license = data
                    self._save_local_license(data)
                    return

            exp_str = data.get("expires_at")
            if exp_str:
                try:
                    exp_dt = datetime.fromisoformat(exp_str)
                    if datetime.utcnow() > exp_dt:
                        data["is_expired"] = True
                        data["is_pro"] = False
                        self._cached_license = data
                        self._save_local_license(data)
                        return
                except Exception:
                    pass

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
        if self._cached_license.get("plan") == "pro_trial":
            claimed, _, is_exp, _ = check_trial_claimed(self.hwid)
            if is_exp:
                self._cached_license["is_expired"] = True
                self._cached_license["is_pro"] = False
                return False
        return bool(self._cached_license.get("is_pro"))

    def get_status(self) -> Dict[str, Any]:
        """Return structured license status for UI display."""
        if not self._cached_license:
            return {
                "is_pro": False,
                "is_trial": False,
                "can_start_trial": self.can_start_trial(),
                "has_claimed_trial": self.has_claimed_trial(),
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

        is_trial = self.is_trial()
        plan_code = self._cached_license.get("plan", "pro")
        plan_title = self._cached_license.get("plan_title", "Pro Plan")
        if is_trial:
            plan_title = "Pro 7-Day Trial"
            days_rem = self.get_trial_days_remaining()

        return {
            "is_pro": self.is_pro(),
            "is_trial": is_trial,
            "can_start_trial": self.can_start_trial(),
            "has_claimed_trial": self.has_claimed_trial(),
            "plan": plan_code,
            "plan_title": plan_title,
            "license_key": self._cached_license.get("license_key", ""),
            "customer_name": self._cached_license.get("customer_name", "Valued Customer"),
            "expires_at": exp_formatted,
            "days_remaining": days_rem,
            "is_expired": bool(self._cached_license.get("is_expired")),
            "hwid": self.hwid
        }


    def has_claimed_trial(self) -> bool:
        """Check if this physical PC has ever claimed the 7-Day Free Trial."""
        claimed, _, _, _ = check_trial_claimed(self.hwid)
        if claimed:
            return True
        if self._cached_license and self._cached_license.get("plan") == "pro_trial":
            return True
        return False

    def is_trial(self) -> bool:
        """Check if current active license is an unexpired 7-Day Free Trial."""
        if not self._cached_license:
            return False
        if self._cached_license.get("is_expired"):
            return False
        if self._cached_license.get("plan") == "pro_trial" or bool(self._cached_license.get("is_trial")):
            claimed, _, is_exp, _ = check_trial_claimed(self.hwid)
            return not is_exp
        return False

    def can_start_trial(self) -> bool:
        """
        Check if this physical PC is eligible to start the 7-Day Free Trial.
        Strict rule: One physical machine can ONLY claim a 7-day trial ONCE for life.
        """
        if self.is_pro():
            return False
        claimed, _, is_exp, _ = check_trial_claimed(self.hwid)
        # If ever claimed, user can NEVER start a fresh trial
        if claimed:
            return False
        return True

    def get_trial_days_remaining(self) -> int:
        """Return number of days remaining on active 7-Day Free Trial (or 0)."""
        if not self.is_trial() or not self._cached_license:
            return 0
        exp_str = self._cached_license.get("expires_at")
        if not exp_str:
            return 7
        try:
            exp_dt = datetime.fromisoformat(exp_str)
            now = datetime.utcnow()
            diff = (exp_dt - now).total_seconds()
            if diff <= 0:
                return 0
            return max(1, int(diff // 86400) + (1 if (diff % 86400) > 0 else 0))
        except Exception:
            return 0

    def start_trial(self) -> Tuple[bool, str]:
        """
        Start the 7-Day Free Trial on this physical computer.
        Enforces strict 1-PC machine lock using Hardware ID (HWID).
        Unlocks all Pro features: 4K 60fps, unlimited playlists, 320k MP3.
        """
        if self.is_pro() and not self.is_trial():
            return False, "You already have an active Pro license activated on this computer!"

        if self.is_trial():
            days = self.get_trial_days_remaining()
            return True, f"Your 7-Day Pro Free Trial is already active ({days} days remaining)!"

        claimed, trial_exp, is_exp, _ = check_trial_claimed(self.hwid)
        if claimed:
            if not is_exp and trial_exp:
                try:
                    exp_dt = datetime.fromisoformat(trial_exp)
                    diff = (exp_dt - datetime.utcnow()).total_seconds()
                    days = max(1, int(diff // 86400) + (1 if (diff % 86400) > 0 else 0))
                    machine_name = socket.gethostname()
                    trial_key = generate_license_key("pro_trial")
                    payload = {
                        "license_key": trial_key,
                        "plan": "pro_trial",
                        "plan_title": "Pro 7-Day Trial",
                        "customer_name": f"Trial User ({machine_name})",
                        "customer_email": "",
                        "hwid": self.hwid,
                        "activated_at": datetime.utcnow().isoformat(),
                        "expires_at": trial_exp,
                        "is_pro": True,
                        "is_trial": True,
                        "is_expired": False
                    }
                    payload["signature"] = sign_license_payload(payload)
                    self._save_local_license(payload)
                    return True, f"Your 7-Day Pro Free Trial is active ({days} days remaining)!"
                except Exception:
                    pass
            return False, "The 7-Day Free Trial has already expired on this computer. Each physical PC is strictly limited to one 7-day trial period for life. Please contact admins on WhatsApp to buy a Pro license."

        machine_name = socket.gethostname()
        now_dt = datetime.utcnow()
        exp_dt = now_dt + timedelta(days=7)
        now_str = now_dt.isoformat()
        exp_str = exp_dt.isoformat()

        # 1. Attempt online server registration
        candidate_urls = get_candidate_server_urls()
        if self.server_url and self.server_url not in candidate_urls:
            candidate_urls.insert(0, self.server_url)

        for base_url in candidate_urls:
            try:
                url = f"{base_url}/api/v1/license/trial"
                resp = requests.post(url, json={"hwid": self.hwid, "machine_name": machine_name}, timeout=3.5)
                if resp.status_code == 200:
                    res_json = resp.json()
                    if res_json.get("status") == "success":
                        data = res_json.get("data", {})
                        data["is_pro"] = True
                        data["is_trial"] = True
                        self._save_local_license(data)
                        record_trial_claim(self.hwid, now_str, data.get("expires_at", exp_str))
                        return True, "🎉 7-Day Pro Free Trial successfully activated on this computer!"
                elif resp.status_code == 400:
                    err_msg = resp.json().get("message", "Trial activation failed.")
                    if "already been claimed" in err_msg.lower():
                        record_trial_claim(self.hwid, now_str, exp_str)
                        return False, err_msg
            except Exception:
                continue

        # 2. Offline cryptographic fallback (100% verified HWID lock)
        trial_key = generate_license_key("pro_trial")
        payload = {
            "license_key": trial_key,
            "plan": "pro_trial",
            "plan_title": "Pro 7-Day Trial",
            "customer_name": f"Trial User ({machine_name})",
            "customer_email": "",
            "hwid": self.hwid,
            "activated_at": now_str,
            "expires_at": exp_str,
            "is_pro": True,
            "is_trial": True
        }
        payload["signature"] = sign_license_payload(payload)
        self._save_local_license(payload)
        record_trial_claim(self.hwid, now_str, exp_str)
        return True, "🎉 7-Day Pro Free Trial successfully activated on this computer! (Offline Verified)"

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

        # ---------------- 1. STRICT HWID REJECTION (NO BACKDOORS) ----------------
        if raw.startswith("HWID-") or raw == self.hwid.upper():
            return False, "This is your computer's Hardware ID (HWID), not a license key. Please enter your official Pro License Key (e.g. MDP-LFT-XXXX-XXXX-SIG) purchased from the seller."

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
