# -*- coding: utf-8 -*-
"""
Script to apply comprehensive security hardening across:
1. backend/database.py
2. backend/server.py
3. licensing.py
4. deploy_vercel/backend/database.py
5. deploy_vercel/backend/server.py
"""
import os
import sys
import shutil

print("[1] Hardening backend/server.py...")

with open("backend/server.py", "r", encoding="utf-8") as f:
    server_code = f.read()

# 1. Update imports in backend/server.py
old_imports = """    delete_admin_user,
    list_admin_users,
    DEFAULT_PLAN_PRICES,"""

new_imports = """    delete_admin_user,
    list_admin_users,
    record_trial_claim,
    get_trial_claim,
    DEFAULT_PLAN_PRICES,"""

if old_imports in server_code:
    server_code = server_code.replace(old_imports, new_imports)
    print("  -> Updated imports in backend/server.py")
else:
    print("  -> Imports already updated or not matched")

# 2. Add HWID reject in api_activate
old_activate = """    if not key or not hwid:
        return jsonify({"status": "error", "message": "License key and Hardware ID (HWID) are required."}), 400

    success, message, lic_dict = activate_license(key, hwid, machine_name)"""

new_activate = """    if not key or not hwid:
        return jsonify({"status": "error", "message": "License key and Hardware ID (HWID) are required."}), 400

    clean_k = key.strip().upper()
    clean_h = hwid.strip().upper()
    if clean_k.startswith("HWID-") or clean_k == clean_h:
        return jsonify({"status": "error", "message": "Machine Hardware ID cannot be used as a license key. Please enter your official Pro License Key (starts with MDP-) issued by the seller."}), 400

    success, message, lic_dict = activate_license(key, hwid, machine_name)"""

if old_activate in server_code:
    server_code = server_code.replace(old_activate, new_activate)
    print("  -> Hardened api_activate in backend/server.py")
else:
    print("  -> api_activate already hardened or not matched")

# 3. Add HWID reject in api_verify
old_verify = """    if not key or not hwid:
        return jsonify({"status": "error", "message": "License key and HWID are required."}), 400

    success, message, lic_dict = verify_license(key, hwid)"""

new_verify = """    if not key or not hwid:
        return jsonify({"status": "error", "message": "License key and HWID are required."}), 400

    clean_k = key.strip().upper()
    clean_h = hwid.strip().upper()
    if clean_k.startswith("HWID-") or clean_k == clean_h:
        return jsonify({"status": "error", "message": "Machine Hardware ID is not a license key."}), 400

    success, message, lic_dict = verify_license(key, hwid)"""

if old_verify in server_code:
    server_code = server_code.replace(old_verify, new_verify)
    print("  -> Hardened api_verify in backend/server.py")
else:
    print("  -> api_verify already hardened or not matched")

# 4. Replace api_trial in backend/server.py
old_trial_start = '@app.route("/api/v1/license/trial", methods=["POST"])'
old_trial_end = 'return jsonify({\n        "status": "success",\n        "message": "🎉 7-Day Pro Free Trial activated successfully on this computer!",\n        "data": payload\n    })'

new_trial_def = '''@app.route("/api/v1/license/trial", methods=["POST"])
def api_trial():
    """Issue or restore 7-Day Free Trial for a physical machine (strictly 1 per HWID for life)."""
    data = request.get_json(silent=True) or {}
    hwid = data.get("hwid", "").strip()
    machine_name = data.get("machine_name", "").strip() or "PC"

    if not hwid:
        return jsonify({"status": "error", "message": "Hardware ID (HWID) is required."}), 400

    clean_hwid = hwid.upper()
    claim = get_trial_claim(clean_hwid)

    if claim:
        exp_str = claim.get("expires_at") or ""
        is_exp = False
        if exp_str:
            try:
                exp_dt = datetime.fromisoformat(exp_str)
                if datetime.utcnow() > exp_dt:
                    is_exp = True
            except Exception:
                pass

        if is_exp:
            return jsonify({
                "status": "error",
                "message": "The 7-Day Free Trial has expired for this computer. Each physical PC is strictly limited to one 7-day trial period for life. Please contact admins on WhatsApp to buy a Pro license."
            }), 400

        # Calculate remaining days
        days_rem = 7
        try:
            exp_dt = datetime.fromisoformat(exp_str)
            diff_secs = (exp_dt - datetime.utcnow()).total_seconds()
            days_rem = max(1, int(diff_secs // 86400) + (1 if (diff_secs % 86400) > 0 else 0))
        except Exception:
            pass

        payload = {
            "license_key": "MDP-TRI-ACTIVE-TRIAL",
            "plan": "pro_trial",
            "plan_title": "Pro 7-Day Trial",
            "customer_name": f"Trial User ({machine_name})",
            "hwid": clean_hwid,
            "created_at": claim.get("claimed_at") or datetime.utcnow().isoformat(),
            "expires_at": exp_str,
            "max_activations": 1,
            "is_pro": 1,
            "is_trial": 1,
            "days_remaining": days_rem,
            "timestamp": datetime.utcnow().isoformat()
        }
        payload["signature"] = sign_license_payload(payload)
        return jsonify({
            "status": "success",
            "message": f"Your 7-Day Pro Free Trial is currently active ({days_rem} days remaining)!",
            "data": payload
        })

    trial_key = generate_license_key("pro_trial")
    exp_dt = calculate_expiry("pro_trial")
    exp_str = exp_dt.isoformat() if exp_dt else ""
    now_str = datetime.utcnow().isoformat()
    client_ip = request.headers.get("X-Forwarded-For", request.remote_addr or "")

    record_trial_claim(clean_hwid, machine_name, now_str, exp_str, client_ip)

    create_license(
        license_key=trial_key,
        plan="pro_trial",
        customer_name=f"Trial User ({machine_name})",
        customer_email="",
        customer_phone="",
        price_paid=0.0,
        is_gift=1,
        payment_method="Free Promotion",
        expires_at=exp_str,
        max_activations=1,
        notes=f"Auto 7-day trial for {clean_hwid}"
    )
    activate_license(trial_key, clean_hwid, machine_name)

    payload = {
        "license_key": trial_key,
        "plan": "pro_trial",
        "plan_title": "Pro 7-Day Trial",
        "customer_name": f"Trial User ({machine_name})",
        "hwid": clean_hwid,
        "created_at": now_str,
        "expires_at": exp_str,
        "max_activations": 1,
        "is_pro": 1,
        "is_trial": 1,
        "days_remaining": 7,
        "timestamp": now_str
    }
    payload["signature"] = sign_license_payload(payload)

    return jsonify({
        "status": "success",
        "message": "🎉 7-Day Pro Free Trial activated successfully on this computer!",
        "data": payload
    })'''

idx_start = server_code.find(old_trial_start)
if idx_start != -1:
    idx_end = server_code.find('    })\n', idx_start)
    if idx_end != -1:
        server_code = server_code[:idx_start] + new_trial_def + server_code[idx_end + len('    })\n'):]
        print("  -> Hardened api_trial in backend/server.py")

with open("backend/server.py", "w", encoding="utf-8") as f:
    f.write(server_code)

print("[2] Hardening licensing.py...")

with open("licensing.py", "r", encoding="utf-8") as f:
    lic_code = f.read()

# Replace record_trial_claim and check_trial_claimed in licensing.py
old_trial_block = """def _get_trial_record_path() -> str:
    folder = os.path.join(os.path.expanduser("~"), ".youtube_downloader")
    os.makedirs(folder, exist_ok=True)
    return os.path.join(folder, "trial_record.dat")


def record_trial_claim(hwid: str, started_at: str, expires_at: str):
    \"\"\"Securely write trial claim to Windows Registry and local protected file.\"\"\"
    # 1. Local file record with HMAC
    try:
        path = _get_trial_record_path()
        payload = {
            "hwid": hwid,
            "trial_started_at": started_at,
            "trial_expires_at": expires_at,
            "claimed": 1
        }
        payload["sig"] = sign_license_payload(payload)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f)
    except Exception:
        pass

    # 2. Windows Registry record (HKCU)
    if sys.platform == "win32":
        try:
            import winreg
            reg_key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\\MediaDownloaderPro")
            winreg.SetValueEx(reg_key, "TrialClaimed", 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(reg_key, "TrialHWID", 0, winreg.REG_SZ, hwid)
            winreg.SetValueEx(reg_key, "TrialExpires", 0, winreg.REG_SZ, expires_at)
            winreg.CloseKey(reg_key)
        except Exception:
            pass


def check_trial_claimed(hwid: str) -> Tuple[bool, Optional[str]]:
    \"\"\"
    Check if this machine (HWID) has ever claimed the 7-day trial.
    Returns (has_claimed: bool, expires_at: Optional[str])
    \"\"\"
    # 1. Check Windows Registry
    if sys.platform == "win32":
        try:
            import winreg
            reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\\MediaDownloaderPro")
            claimed, _ = winreg.QueryValueEx(reg_key, "TrialClaimed")
            reg_hwid, _ = winreg.QueryValueEx(reg_key, "TrialHWID")
            reg_exp, _ = winreg.QueryValueEx(reg_key, "TrialExpires")
            winreg.CloseKey(reg_key)
            if claimed == 1 and (reg_hwid == hwid or not reg_hwid):
                return True, reg_exp
        except Exception:
            pass

    # 2. Check local file
    try:
        path = _get_trial_record_path()
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if data.get("hwid") == hwid and data.get("claimed") == 1:
                return True, data.get("trial_expires_at")
    except Exception:
        pass

    return False, None"""

new_trial_block = """def _get_system_trial_marker_path() -> str:
    \"\"\"Return machine-wide persistent storage path that survives user profile resets and app uninstallation.\"\"\"
    program_data = os.environ.get("ALLUSERSPROFILE") or os.environ.get("ProgramData") or r"C:\\ProgramData"
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
    \"\"\"
    Multi-Tier Permanent Machine Trial Lock:
    Permanently writes the trial claim across 4 independent persistence layers:
    1. Machine-Wide System Directory (ProgramData) - Survives uninstallation and user profile switches.
    2. Windows Registry Primary Key (HKCU\\Software\\MediaDownloaderPro).
    3. Windows Registry Secondary Stealth Key (HKCU\\Software\\AppDataSystem\\MDP_Core).
    4. Local User AppData Directory (~/.youtube_downloader/trial_record.dat).
    \"\"\"
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
            reg_key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\\MediaDownloaderPro")
            winreg.SetValueEx(reg_key, "TrialClaimed", 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(reg_key, "TrialHWID", 0, winreg.REG_SZ, clean_hwid)
            winreg.SetValueEx(reg_key, "TrialStarted", 0, winreg.REG_SZ, started_at)
            winreg.SetValueEx(reg_key, "TrialExpires", 0, winreg.REG_SZ, expires_at)
            winreg.SetValueEx(reg_key, "ClockWatermark", 0, winreg.REG_SZ, clock_mark)
            winreg.CloseKey(reg_key)

            # Secondary Stealth Key
            stealth_key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\\AppDataSystem\\MDP_Core")
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
    \"\"\"
    Check if this physical machine (HWID) has ever claimed the 7-day trial across all 4 persistence layers.
    Includes Clock Rollback / Anti-Tampering Protection.
    Returns: (has_claimed: bool, expires_at: Optional[str], is_expired: bool, reason: str)
    \"\"\"
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
            reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\\MediaDownloaderPro")
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
            stealth_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\\AppDataSystem\\MDP_Core")
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
    return True, target_expires, is_expired, reason"""

if old_trial_block in lic_code:
    lic_code = lic_code.replace(old_trial_block, new_trial_block)
    print("  -> Updated record_trial_claim and check_trial_claimed in licensing.py")
else:
    print("  -> Could not find old trial block in licensing.py (checking normalized whitespace)")
    # Normalize \r\n
    lic_code_norm = lic_code.replace("\r\n", "\n")
    old_trial_norm = old_trial_block.replace("\r\n", "\n")
    if old_trial_norm in lic_code_norm:
        lic_code = lic_code_norm.replace(old_trial_norm, new_trial_block)
        print("  -> Replaced normalized trial block in licensing.py")

# Update LicenseManager._load_local_license
old_load = """        if not os.path.isfile(self.license_path):
            claimed, trial_exp = check_trial_claimed(self.hwid)
            if claimed and trial_exp:
                try:
                    exp_dt = datetime.fromisoformat(trial_exp)
                    if datetime.utcnow() < exp_dt:
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
            return"""

new_load = """        if not os.path.isfile(self.license_path):
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
            return"""

lic_code = lic_code.replace("\r\n", "\n")
if old_load.replace("\r\n", "\n") in lic_code:
    lic_code = lic_code.replace(old_load.replace("\r\n", "\n"), new_load)
    print("  -> Updated _load_local_license initial check")

# In _load_local_license, check for trial expiration on cached license
old_exp_check = """            # 3. Expiration check
            exp_str = data.get("expires_at")
            if exp_str:
                exp_dt = datetime.fromisoformat(exp_str)
                if datetime.utcnow() > exp_dt:
                    # License expired
                    data["is_expired"] = True
                    self._cached_license = data
                    return"""

new_exp_check = """            # 3. Expiration check & Trial lockdown check
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
                    pass"""

if old_exp_check.replace("\r\n", "\n") in lic_code:
    lic_code = lic_code.replace(old_exp_check.replace("\r\n", "\n"), new_exp_check)
    print("  -> Updated _load_local_license expiration check")

# In is_pro, check trial validity dynamically
old_is_pro = """    def is_pro(self) -> bool:
        \"\"\"Check if Pro plan is currently active and valid.\"\"\"
        if not self._cached_license:
            return False
        if self._cached_license.get("is_expired"):
            return False
        return bool(self._cached_license.get("is_pro"))"""

new_is_pro = """    def is_pro(self) -> bool:
        \"\"\"Check if Pro plan is currently active and valid.\"\"\"
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
        return bool(self._cached_license.get("is_pro"))"""

if old_is_pro.replace("\r\n", "\n") in lic_code:
    lic_code = lic_code.replace(old_is_pro.replace("\r\n", "\n"), new_is_pro)
    print("  -> Hardened is_pro in licensing.py")

# In has_claimed_trial and can_start_trial
old_trial_methods = """    def has_claimed_trial(self) -> bool:
        \"\"\"Check if this physical PC has ever claimed the 7-Day Free Trial.\"\"\"
        claimed, _ = check_trial_claimed(self.hwid)
        if claimed:
            return True
        if self._cached_license and self._cached_license.get("plan") == "pro_trial":
            return True
        return False

    def is_trial(self) -> bool:
        \"\"\"Check if current active license is an unexpired 7-Day Free Trial.\"\"\"
        if not self._cached_license:
            return False
        if self._cached_license.get("is_expired"):
            return False
        return self._cached_license.get("plan") == "pro_trial" or bool(self._cached_license.get("is_trial"))

    def can_start_trial(self) -> bool:
        \"\"\"Check if this computer is eligible to start the 7-Day Free Trial.\"\"\"
        if self.is_pro():
            return False
        claimed, trial_exp = check_trial_claimed(self.hwid)
        if not claimed:
            return True
        if trial_exp:
            try:
                if datetime.utcnow() < datetime.fromisoformat(trial_exp):
                    return True
            except Exception:
                pass
        return False"""

new_trial_methods = """    def has_claimed_trial(self) -> bool:
        \"\"\"Check if this physical PC has ever claimed the 7-Day Free Trial.\"\"\"
        claimed, _, _, _ = check_trial_claimed(self.hwid)
        if claimed:
            return True
        if self._cached_license and self._cached_license.get("plan") == "pro_trial":
            return True
        return False

    def is_trial(self) -> bool:
        \"\"\"Check if current active license is an unexpired 7-Day Free Trial.\"\"\"
        if not self._cached_license:
            return False
        if self._cached_license.get("is_expired"):
            return False
        if self._cached_license.get("plan") == "pro_trial" or bool(self._cached_license.get("is_trial")):
            claimed, _, is_exp, _ = check_trial_claimed(self.hwid)
            return not is_exp
        return False

    def can_start_trial(self) -> bool:
        \"\"\"
        Check if this physical PC is eligible to start the 7-Day Free Trial.
        Strict rule: One physical machine can ONLY claim a 7-day trial ONCE for life.
        \"\"\"
        if self.is_pro():
            return False
        claimed, _, is_exp, _ = check_trial_claimed(self.hwid)
        # If ever claimed, user can NEVER start a fresh trial
        if claimed:
            return False
        return True"""

if old_trial_methods.replace("\r\n", "\n") in lic_code:
    lic_code = lic_code.replace(old_trial_methods.replace("\r\n", "\n"), new_trial_methods)
    print("  -> Hardened can_start_trial and is_trial in licensing.py")

# Update start_trial in licensing.py
old_start_trial_target = """        claimed, trial_exp = check_trial_claimed(self.hwid)
        if claimed:
            if trial_exp:
                try:
                    exp_dt = datetime.fromisoformat(trial_exp)
                    if datetime.utcnow() < exp_dt:
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
            return False, "The 7-Day Free Trial has already been claimed on this computer. Please purchase a Pro license to continue enjoying 4K 60fps & Playlists.\""""

new_start_trial_target = """        claimed, trial_exp, is_exp, _ = check_trial_claimed(self.hwid)
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
            return False, "The 7-Day Free Trial has already expired on this computer. Each physical PC is strictly limited to one 7-day trial period for life. Please contact admins on WhatsApp to buy a Pro license.\""""

if old_start_trial_target.replace("\r\n", "\n") in lic_code:
    lic_code = lic_code.replace(old_start_trial_target.replace("\r\n", "\n"), new_start_trial_target)
    print("  -> Hardened start_trial claim check in licensing.py")

# Update activate() in licensing.py to completely eliminate the HWID backdoor!
old_activate_def = """        # ---------------- 1. DIRECT HWID ACTIVATION ----------------
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

        # ---------------- 2. FORMAT AND SANITIZE KEY ----------------"""

new_activate_def = """        # ---------------- 1. STRICT HWID REJECTION (NO BACKDOORS) ----------------
        if raw.startswith("HWID-") or raw == self.hwid.upper():
            return False, "This is your computer's Hardware ID (HWID), not a license key. Please enter your official Pro License Key (e.g. MDP-LFT-XXXX-XXXX-SIG) purchased from the seller."

        # ---------------- 2. FORMAT AND SANITIZE KEY ----------------"""

if old_activate_def.replace("\r\n", "\n") in lic_code:
    lic_code = lic_code.replace(old_activate_def.replace("\r\n", "\n"), new_activate_def)
    print("  -> REMOVED HWID ACTIVATION BACKDOOR from licensing.py!")

with open("licensing.py", "w", encoding="utf-8") as f:
    f.write(lic_code)

print("[3] Syncing to deploy_vercel...")
shutil.copy2("backend/database.py", "deploy_vercel/backend/database.py")
shutil.copy2("backend/server.py", "deploy_vercel/backend/server.py")
print("  -> Synced database.py and server.py to deploy_vercel/backend/")

print("[DONE] Security hardening script applied.")
