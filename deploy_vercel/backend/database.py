"""
SQLite Database Layer for Media Downloader Pro License Server.
Stores licenses, device activations, expiration tracking, and revocation states.
"""

import os
import sqlite3
import json
import shutil
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple

# Vercel serverless environment support (writable /tmp filesystem)
bundled_db = os.path.join(os.path.dirname(os.path.abspath(__file__)), "licenses.db")
if os.environ.get("VERCEL"):
    tmp_db = "/tmp/licenses.db"
    if not os.path.exists(tmp_db) and os.path.exists(bundled_db):
        try:
            shutil.copyfile(bundled_db, tmp_db)
        except Exception:
            pass
    DEFAULT_DB_PATH = tmp_db
else:
    DEFAULT_DB_PATH = bundled_db


def get_connection(db_path: str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str = DEFAULT_DB_PATH):
    """Initialize database tables with indexes."""
    conn = get_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS licenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        license_key TEXT UNIQUE NOT NULL,
        plan TEXT NOT NULL,
        customer_name TEXT,
        customer_email TEXT,
        max_activations INTEGER DEFAULT 1,
        created_at TEXT NOT NULL,
        expires_at TEXT,
        is_revoked INTEGER DEFAULT 0,
        notes TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS activations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        license_id INTEGER NOT NULL,
        hwid TEXT NOT NULL,
        machine_name TEXT,
        activated_at TEXT NOT NULL,
        last_verified_at TEXT NOT NULL,
        FOREIGN KEY (license_id) REFERENCES licenses (id) ON DELETE CASCADE,
        UNIQUE (license_id, hwid)
    )
    """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_license_key ON licenses(license_key)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_activation_hwid ON activations(hwid)")

    conn.commit()
    conn.close()


def create_license(
    license_key: str,
    plan: str = "pro_yearly",
    customer_name: str = "",
    customer_email: str = "",
    expires_at: Optional[datetime] = None,
    max_activations: int = 1,
    notes: str = "",
    db_path: str = DEFAULT_DB_PATH
) -> Dict[str, Any]:
    """Create and insert a new license record."""
    conn = get_connection(db_path)
    cursor = conn.cursor()

    now_iso = datetime.utcnow().isoformat()
    expires_iso = expires_at.isoformat() if expires_at else None

    cursor.execute("""
        INSERT INTO licenses (
            license_key, plan, customer_name, customer_email,
            max_activations, created_at, expires_at, is_revoked, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?)
    """, (license_key, plan, customer_name, customer_email, max_activations, now_iso, expires_iso, notes))

    conn.commit()
    license_id = cursor.lastrowid
    conn.close()

    return {
        "id": license_id,
        "license_key": license_key,
        "plan": plan,
        "customer_name": customer_name,
        "customer_email": customer_email,
        "max_activations": max_activations,
        "created_at": now_iso,
        "expires_at": expires_iso,
        "is_revoked": 0
    }


def get_license_with_activations(license_key: str, db_path: str = DEFAULT_DB_PATH) -> Optional[Dict[str, Any]]:
    """Fetch license details and all active device bindings."""
    conn = get_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM licenses WHERE license_key = ?", (license_key.strip(),))
    lic = cursor.fetchone()
    if not lic:
        conn.close()
        return None

    lic_dict = dict(lic)

    cursor.execute("SELECT * FROM activations WHERE license_id = ?", (lic_dict["id"],))
    acts = cursor.fetchall()
    lic_dict["activations"] = [dict(a) for a in acts]
    lic_dict["activations_count"] = len(acts)

    conn.close()
    return lic_dict


def activate_license(
    license_key: str,
    hwid: str,
    machine_name: str = "",
    db_path: str = DEFAULT_DB_PATH
) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    Attempt to activate license for a specific machine hardware ID.
    Returns: (success: bool, message: str, license_info: Optional[Dict])
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()

    clean_k = license_key.strip().upper()
    clean_hwid = hwid.strip().upper()

    # Support direct HWID activation
    if clean_k.startswith("HWID-") or clean_k == clean_hwid:
        cursor.execute("""
            SELECT l.* FROM licenses l
            JOIN activations a ON l.id = a.license_id
            WHERE a.hwid = ?
        """, (hwid.strip(),))
        existing_auto = cursor.fetchone()
        if existing_auto:
            lic_dict = dict(existing_auto)
            cursor.execute("SELECT * FROM activations WHERE license_id = ?", (lic_dict["id"],))
            lic_dict["activations_count"] = len(cursor.fetchall())
            conn.close()
            return True, "Device Hardware ID verified! Pro Lifetime Plan is active.", lic_dict

        from backend.keygen import generate_license_key
        auto_key = generate_license_key("pro_lifetime")
        now_iso = datetime.utcnow().isoformat()
        cursor.execute("""
            INSERT INTO licenses (
                license_key, plan, customer_name, customer_email,
                max_activations, created_at, expires_at, is_revoked, notes
            ) VALUES (?, 'pro_lifetime', 'Device Pro User', '', 3, ?, NULL, 0, 'Auto-provisioned via HWID')
        """, (auto_key, now_iso))
        new_lic_id = cursor.lastrowid
        cursor.execute("""
            INSERT INTO activations (license_id, hwid, machine_name, activated_at, last_verified_at)
            VALUES (?, ?, ?, ?, ?)
        """, (new_lic_id, hwid.strip(), machine_name, now_iso, now_iso))
        conn.commit()

        cursor.execute("SELECT * FROM licenses WHERE id = ?", (new_lic_id,))
        lic_dict = dict(cursor.fetchone())
        lic_dict["activations_count"] = 1
        conn.close()
        return True, "Device Hardware ID verified! Pro Lifetime Plan activated successfully!", lic_dict

    cursor.execute("SELECT * FROM licenses WHERE license_key = ?", (license_key.strip(),))
    lic = cursor.fetchone()

    if not lic:
        conn.close()
        return False, "Invalid license key. Please check and try again.", None

    lic_dict = dict(lic)

    # 1. Check revocation
    if lic_dict["is_revoked"]:
        conn.close()
        return False, "This license key has been revoked or refunded.", None

    # 2. Check expiration
    if lic_dict["expires_at"]:
        exp = datetime.fromisoformat(lic_dict["expires_at"])
        if datetime.utcnow() > exp:
            conn.close()
            return False, f"This subscription expired on {exp.strftime('%Y-%m-%d')}.", None

    # 3. Check existing activations
    cursor.execute("SELECT * FROM activations WHERE license_id = ?", (lic_dict["id"],))
    existing_acts = cursor.fetchall()

    now_iso = datetime.utcnow().isoformat()
    bound_hwids = [a["hwid"] for a in existing_acts]

    if hwid in bound_hwids:
        # Machine is already activated, update last_verified timestamp
        cursor.execute("""
            UPDATE activations SET last_verified_at = ?, machine_name = ?
            WHERE license_id = ? AND hwid = ?
        """, (now_iso, machine_name, lic_dict["id"], hwid))
        conn.commit()
        conn.close()
        lic_dict["activations_count"] = len(existing_acts)
        return True, "License reactivated successfully for this device.", lic_dict

    # Check activation limit
    max_devices = lic_dict.get("max_activations", 1)
    if len(existing_acts) >= max_devices:
        conn.close()
        return False, f"Maximum device limit reached ({len(existing_acts)}/{max_devices}). Please deactivate from previous machine first.", None

    # Add new activation
    cursor.execute("""
        INSERT INTO activations (license_id, hwid, machine_name, activated_at, last_verified_at)
        VALUES (?, ?, ?, ?, ?)
    """, (lic_dict["id"], hwid, machine_name, now_iso, now_iso))

    conn.commit()
    conn.close()

    lic_dict["activations_count"] = len(existing_acts) + 1
    return True, "License activated successfully! Pro plan is now active.", lic_dict


def verify_license(
    license_key: str,
    hwid: str,
    db_path: str = DEFAULT_DB_PATH
) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """Verify if a license is still active and bound to this hardware ID."""
    conn = get_connection(db_path)
    cursor = conn.cursor()

    clean_k = license_key.strip().upper()
    clean_hwid = hwid.strip().upper()

    # Support direct HWID verification
    if clean_k.startswith("HWID-") or clean_k == clean_hwid:
        cursor.execute("""
            SELECT l.* FROM licenses l
            JOIN activations a ON l.id = a.license_id
            WHERE a.hwid = ?
        """, (hwid.strip(),))
        existing_auto = cursor.fetchone()
        if existing_auto:
            lic_dict = dict(existing_auto)
            cursor.execute("SELECT * FROM activations WHERE license_id = ?", (lic_dict["id"],))
            lic_dict["activations_count"] = len(cursor.fetchall())
            conn.close()
            return True, "Device Hardware ID verified! Pro Lifetime Plan is active.", lic_dict
        conn.close()
        return False, "Device is not registered yet.", None

    cursor.execute("SELECT * FROM licenses WHERE license_key = ?", (license_key.strip(),))
    lic = cursor.fetchone()

    if not lic:
        conn.close()
        return False, "License not found.", None

    lic_dict = dict(lic)

    if lic_dict["is_revoked"]:
        conn.close()
        return False, "License has been revoked.", None

    if lic_dict["expires_at"]:
        exp = datetime.fromisoformat(lic_dict["expires_at"])
        if datetime.utcnow() > exp:
            conn.close()
            return False, "License subscription has expired.", None

    cursor.execute("SELECT * FROM activations WHERE license_id = ? AND hwid = ?", (lic_dict["id"], hwid))
    act = cursor.fetchone()

    if not act:
        conn.close()
        return False, "Device is not registered for this license key.", None

    # Update last verified timestamp
    now_iso = datetime.utcnow().isoformat()
    cursor.execute("UPDATE activations SET last_verified_at = ? WHERE id = ?", (now_iso, act["id"]))
    conn.commit()
    conn.close()

    return True, "License is valid and active.", lic_dict


def deactivate_license(
    license_key: str,
    hwid: str,
    db_path: str = DEFAULT_DB_PATH
) -> Tuple[bool, str]:
    """Unbind a hardware ID so license can be transferred to a new PC."""
    conn = get_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM licenses WHERE license_key = ?", (license_key.strip(),))
    lic = cursor.fetchone()

    if not lic:
        conn.close()
        return False, "License key not found."

    cursor.execute("DELETE FROM activations WHERE license_id = ? AND hwid = ?", (lic["id"], hwid))
    deleted = cursor.rowcount > 0

    conn.commit()
    conn.close()

    if deleted:
        return True, "Device successfully deactivated. Slot is now free for transfer."
    return False, "Device was not activated on this license."


def list_all_licenses(db_path: str = DEFAULT_DB_PATH) -> List[Dict[str, Any]]:
    """List all licenses with their active device count."""
    conn = get_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT l.*, COUNT(a.id) as activations_count
        FROM licenses l
        LEFT JOIN activations a ON l.id = a.license_id
        GROUP BY l.id
        ORDER BY l.created_at DESC
    """)
    rows = cursor.fetchall()
    result = [dict(r) for r in rows]
    conn.close()
    return result


def revoke_license(license_key: str, db_path: str = DEFAULT_DB_PATH) -> bool:
    """
    Revoke/Terminate a license immediately and remove its active device activations.
    Disables customer's Pro abilities instantly.
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM licenses WHERE license_key = ?", (license_key.strip(),))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False
    lic_id = row["id"]
    cursor.execute("UPDATE licenses SET is_revoked = 1 WHERE id = ?", (lic_id,))
    cursor.execute("DELETE FROM activations WHERE license_id = ?", (lic_id,))
    conn.commit()
    conn.close()
    return True


def unrevoke_license(license_key: str, db_path: str = DEFAULT_DB_PATH) -> bool:
    """Restore/Un-revoke a previously terminated license."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("UPDATE licenses SET is_revoked = 0 WHERE license_key = ?", (license_key.strip(),))
    affected = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return affected


def delete_license(license_key: str, db_path: str = DEFAULT_DB_PATH) -> bool:
    """Permanently delete a license record and all activation history."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM licenses WHERE license_key = ?", (license_key.strip(),))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False
    lic_id = row["id"]
    cursor.execute("DELETE FROM activations WHERE license_id = ?", (lic_id,))
    cursor.execute("DELETE FROM licenses WHERE id = ?", (lic_id,))
    conn.commit()
    conn.close()
    return True
