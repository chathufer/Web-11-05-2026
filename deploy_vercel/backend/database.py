"""
SQLite Database Layer for Media Downloader Pro License Server.
Stores licenses, device activations, expiration tracking, sales data, and revocation states.
"""

import os
import sqlite3
import json
import shutil
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple

# Default Plan Pricing in USD
DEFAULT_PLAN_PRICES = {
    "pro_monthly": 1.99,
    "pro_yearly": 14.99,
    "pro_lifetime": 24.99,
    "pro_trial": 0.0,
    "pro_custom": 0.0
}

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
    """Initialize database tables with indexes and safe schema migrations."""
    conn = get_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS licenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        license_key TEXT UNIQUE NOT NULL,
        plan TEXT NOT NULL,
        customer_name TEXT,
        customer_email TEXT,
        customer_phone TEXT DEFAULT '',
        price_paid REAL DEFAULT 0.0,
        payment_method TEXT DEFAULT 'WhatsApp / Admin',
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

    # Safe schema migration for older DBs
    cursor.execute("PRAGMA table_info(licenses)")
    columns = [col[1] for col in cursor.fetchall()]
    if "price_paid" not in columns:
        try:
            cursor.execute("ALTER TABLE licenses ADD COLUMN price_paid REAL DEFAULT 0.0")
        except Exception:
            pass
    if "customer_phone" not in columns:
        try:
            cursor.execute("ALTER TABLE licenses ADD COLUMN customer_phone TEXT DEFAULT ''")
        except Exception:
            pass
    if "payment_method" not in columns:
        try:
            cursor.execute("ALTER TABLE licenses ADD COLUMN payment_method TEXT DEFAULT 'WhatsApp / Admin'")
        except Exception:
            pass

    # Retroactively backfill price_paid for older existing licenses if 0.0
    try:
        cursor.execute("UPDATE licenses SET price_paid = 24.99 WHERE (price_paid IS NULL OR price_paid = 0.0) AND plan = 'pro_lifetime'")
        cursor.execute("UPDATE licenses SET price_paid = 14.99 WHERE (price_paid IS NULL OR price_paid = 0.0) AND plan = 'pro_yearly'")
        cursor.execute("UPDATE licenses SET price_paid = 1.99 WHERE (price_paid IS NULL OR price_paid = 0.0) AND plan = 'pro_monthly'")
    except Exception:
        pass

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_license_key ON licenses(license_key)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_activation_hwid ON activations(hwid)")

    conn.commit()
    conn.close()


def create_license(
    license_key: str,
    plan: str = "pro_yearly",
    customer_name: str = "",
    customer_email: str = "",
    customer_phone: str = "",
    price_paid: Optional[float] = None,
    payment_method: str = "WhatsApp / Admin",
    expires_at: Optional[datetime] = None,
    max_activations: int = 1,
    notes: str = "",
    db_path: str = DEFAULT_DB_PATH
) -> Dict[str, Any]:
    """Create and insert a new license record with sales tracking."""
    conn = get_connection(db_path)
    cursor = conn.cursor()

    now_iso = datetime.utcnow().isoformat()
    expires_iso = expires_at.isoformat() if isinstance(expires_at, datetime) else (expires_at if expires_at else None)

    if price_paid is None or price_paid == 0.0:
        if plan != "pro_trial":
            price_paid = DEFAULT_PLAN_PRICES.get(plan, 0.0)
        else:
            price_paid = 0.0

    cursor.execute("""
        INSERT INTO licenses (
            license_key, plan, customer_name, customer_email, customer_phone,
            price_paid, payment_method, max_activations, created_at, expires_at,
            is_revoked, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?)
    """, (
        license_key, plan, customer_name, customer_email, customer_phone,
        float(price_paid), payment_method, max_activations, now_iso, expires_iso, notes
    ))

    conn.commit()
    license_id = cursor.lastrowid
    conn.close()

    return {
        "id": license_id,
        "license_key": license_key,
        "plan": plan,
        "customer_name": customer_name,
        "customer_email": customer_email,
        "customer_phone": customer_phone,
        "price_paid": float(price_paid),
        "payment_method": payment_method,
        "max_activations": max_activations,
        "created_at": now_iso,
        "expires_at": expires_iso,
        "is_revoked": 0,
        "notes": notes
    }


def update_license(
    license_key: str,
    plan: Optional[str] = None,
    customer_name: Optional[str] = None,
    customer_email: Optional[str] = None,
    customer_phone: Optional[str] = None,
    expires_at: Optional[str] = None,
    max_activations: Optional[int] = None,
    price_paid: Optional[float] = None,
    payment_method: Optional[str] = None,
    notes: Optional[str] = None,
    db_path: str = DEFAULT_DB_PATH
) -> bool:
    """Update editable fields of an existing license."""
    conn = get_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM licenses WHERE license_key = ?", (license_key.strip(),))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False

    updates = []
    params = []

    if plan is not None:
        updates.append("plan = ?")
        params.append(plan)
    if customer_name is not None:
        updates.append("customer_name = ?")
        params.append(customer_name)
    if customer_email is not None:
        updates.append("customer_email = ?")
        params.append(customer_email)
    if customer_phone is not None:
        updates.append("customer_phone = ?")
        params.append(customer_phone)
    if expires_at is not None:
        updates.append("expires_at = ?")
        params.append(expires_at if expires_at != "LIFETIME" else None)
    if max_activations is not None:
        updates.append("max_activations = ?")
        params.append(int(max_activations))
    if price_paid is not None:
        updates.append("price_paid = ?")
        params.append(float(price_paid))
    if payment_method is not None:
        updates.append("payment_method = ?")
        params.append(payment_method)
    if notes is not None:
        updates.append("notes = ?")
        params.append(notes)

    if not updates:
        conn.close()
        return True

    params.append(license_key.strip())
    query = f"UPDATE licenses SET {', '.join(updates)} WHERE license_key = ?"
    cursor.execute(query, tuple(params))
    conn.commit()
    conn.close()
    return True


def extend_license(
    license_key: str,
    add_days: int = 0,
    make_lifetime: bool = False,
    db_path: str = DEFAULT_DB_PATH
) -> Tuple[bool, str, Optional[str]]:
    """Extend expiration of a license by N days or convert it to Lifetime."""
    conn = get_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM licenses WHERE license_key = ?", (license_key.strip(),))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False, "License not found.", None

    lic = dict(row)

    if make_lifetime:
        cursor.execute("UPDATE licenses SET expires_at = NULL, plan = 'pro_lifetime' WHERE id = ?", (lic["id"],))
        conn.commit()
        conn.close()
        return True, "License successfully converted to Lifetime (Never Expires).", "Lifetime"

    # Calculate new expiration date
    current_exp = lic.get("expires_at")
    base_dt = datetime.utcnow()
    if current_exp:
        try:
            parsed = datetime.fromisoformat(current_exp)
            if parsed > base_dt:
                base_dt = parsed
        except Exception:
            pass

    new_exp_dt = base_dt + timedelta(days=add_days)
    new_exp_iso = new_exp_dt.isoformat()

    cursor.execute("UPDATE licenses SET expires_at = ?, is_revoked = 0 WHERE id = ?", (new_exp_iso, lic["id"]))
    conn.commit()
    conn.close()
    return True, f"License successfully extended by {add_days} days until {new_exp_dt.strftime('%Y-%m-%d')}.", new_exp_iso


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

    cursor.execute("SELECT * FROM activations WHERE license_id = ? ORDER BY activated_at DESC", (lic_dict["id"],))
    acts = cursor.fetchall()
    lic_dict["activations"] = [dict(a) for a in acts]
    lic_dict["activations_count"] = len(acts)

    conn.close()
    return lic_dict


def deactivate_device_by_id(activation_id: int, db_path: str = DEFAULT_DB_PATH) -> bool:
    """Unbind a specific device activation by its record ID."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM activations WHERE id = ?", (activation_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted


def reset_all_devices(license_key: str, db_path: str = DEFAULT_DB_PATH) -> int:
    """Clear all device activations for a license so customer can bind new PCs."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM licenses WHERE license_key = ?", (license_key.strip(),))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return 0

    cursor.execute("DELETE FROM activations WHERE license_id = ?", (row["id"],))
    deleted_count = cursor.rowcount
    conn.commit()
    conn.close()
    return deleted_count


def lookup_hwid(query: str, db_path: str = DEFAULT_DB_PATH) -> List[Dict[str, Any]]:
    """Search activations and licenses by HWID, machine name, or customer info."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    clean_q = f"%{query.strip()}%"

    cursor.execute("""
        SELECT a.id as activation_id, a.hwid, a.machine_name, a.activated_at, a.last_verified_at,
               l.id as license_id, l.license_key, l.plan, l.customer_name, l.customer_phone,
               l.customer_email, l.is_revoked, l.expires_at, l.max_activations
        FROM activations a
        JOIN licenses l ON a.license_id = l.id
        WHERE a.hwid LIKE ? OR a.machine_name LIKE ? OR l.license_key LIKE ? OR l.customer_name LIKE ?
        ORDER BY a.last_verified_at DESC
    """, (clean_q, clean_q, clean_q, clean_q))

    rows = cursor.fetchall()
    result = [dict(r) for r in rows]
    conn.close()
    return result


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
                license_key, plan, customer_name, customer_email, customer_phone,
                price_paid, payment_method, max_activations, created_at, expires_at,
                is_revoked, notes
            ) VALUES (?, 'pro_lifetime', 'Device Pro User', '', '', 24.99, 'Direct HWID Activation', 3, ?, NULL, 0, 'Auto-provisioned via HWID')
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
        try:
            exp = datetime.fromisoformat(lic_dict["expires_at"])
            if datetime.utcnow() > exp:
                conn.close()
                return False, f"This subscription expired on {exp.strftime('%Y-%m-%d')}.", None
        except Exception:
            pass

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
        return False, f"Maximum device limit reached ({len(existing_acts)}/{max_devices}). Contact admin in WhatsApp to transfer or reset your device slot.", None

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
        try:
            exp = datetime.fromisoformat(lic_dict["expires_at"])
            if datetime.utcnow() > exp:
                conn.close()
                return False, "License subscription has expired.", None
        except Exception:
            pass

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


def list_all_licenses(
    search_q: str = "",
    plan_filter: str = "",
    status_filter: str = "",
    db_path: str = DEFAULT_DB_PATH
) -> List[Dict[str, Any]]:
    """List all licenses with search, filtering, and active device counts."""
    conn = get_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT l.*,
               COUNT(a.id) as activations_count,
               GROUP_CONCAT(COALESCE(a.machine_name, a.hwid), ' | ') as bound_machines,
               GROUP_CONCAT(a.hwid, ', ') as bound_hwids
        FROM licenses l
        LEFT JOIN activations a ON l.id = a.license_id
        GROUP BY l.id
        ORDER BY l.created_at DESC
    """)
    rows = cursor.fetchall()
    conn.close()

    now_dt = datetime.utcnow()
    results = []

    for r in rows:
        item = dict(r)
        key = item.get("license_key", "")
        name = item.get("customer_name", "") or ""
        email = item.get("customer_email", "") or ""
        phone = item.get("customer_phone", "") or ""
        notes = item.get("notes", "") or ""
        plan = item.get("plan", "")
        hwids = item.get("bound_hwids", "") or ""
        machines = item.get("bound_machines", "") or ""

        # Status computation
        if item.get("is_revoked"):
            status = "revoked"
        elif item.get("expires_at"):
            try:
                exp = datetime.fromisoformat(item["expires_at"])
                status = "expired" if now_dt > exp else ("trial" if plan == "pro_trial" else "active")
            except Exception:
                status = "active"
        else:
            status = "trial" if plan == "pro_trial" else "active"

        item["computed_status"] = status

        # Search filter
        if search_q:
            sq = search_q.lower()
            haystack = f"{key} {name} {email} {phone} {notes} {hwids} {machines}".lower()
            if sq not in haystack:
                continue

        # Plan filter
        if plan_filter and plan_filter != "all":
            if item.get("plan") != plan_filter:
                continue

        # Status filter
        if status_filter and status_filter != "all":
            if status != status_filter:
                continue

        results.append(item)

    return results


def get_sales_analytics(db_path: str = DEFAULT_DB_PATH) -> Dict[str, Any]:
    """Compute comprehensive sales, revenue, and license statistics."""
    conn = get_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM licenses")
    all_licenses = [dict(r) for r in cursor.fetchall()]

    cursor.execute("SELECT COUNT(*) FROM activations")
    total_active_devices = cursor.fetchone()[0]

    conn.close()

    now_dt = datetime.utcnow()
    now_month_prefix = now_dt.strftime("%Y-%m")
    now_today_prefix = now_dt.strftime("%Y-%m-%d")

    total_revenue = 0.0
    month_revenue = 0.0
    today_revenue = 0.0

    active_count = 0
    expired_count = 0
    revoked_count = 0
    trials_count = 0

    plans_breakdown = {
        "pro_lifetime": {"count": 0, "revenue": 0.0, "name": "Lifetime Master Pass ($24.99)"},
        "pro_yearly": {"count": 0, "revenue": 0.0, "name": "Annual Pro Pass ($14.99)"},
        "pro_monthly": {"count": 0, "revenue": 0.0, "name": "Monthly Pro Pass ($1.99)"},
        "pro_trial": {"count": 0, "revenue": 0.0, "name": "7-Day Free Trial ($0.00)"},
        "pro_custom": {"count": 0, "revenue": 0.0, "name": "Custom License"}
    }

    for lic in all_licenses:
        plan = lic.get("plan", "pro_lifetime")
        price = float(lic.get("price_paid") or 0.0)
        is_rev = bool(lic.get("is_revoked"))
        created = lic.get("created_at", "")

        # Compute status
        if is_rev:
            revoked_count += 1
        elif lic.get("expires_at"):
            try:
                exp = datetime.fromisoformat(lic["expires_at"])
                if now_dt > exp:
                    expired_count += 1
                else:
                    if plan == "pro_trial":
                        trials_count += 1
                    else:
                        active_count += 1
            except Exception:
                active_count += 1
        else:
            if plan == "pro_trial":
                trials_count += 1
            else:
                active_count += 1

        # Revenue counting (only non-revoked orders)
        if not is_rev and plan != "pro_trial":
            total_revenue += price
            if created.startswith(now_month_prefix):
                month_revenue += price
            if created.startswith(now_today_prefix):
                today_revenue += price

        if plan in plans_breakdown:
            plans_breakdown[plan]["count"] += 1
            if not is_rev:
                plans_breakdown[plan]["revenue"] += price
        else:
            plans_breakdown["pro_custom"]["count"] += 1
            if not is_rev:
                plans_breakdown["pro_custom"]["revenue"] += price

    return {
        "total_revenue": round(total_revenue, 2),
        "month_revenue": round(month_revenue, 2),
        "today_revenue": round(today_revenue, 2),
        "total_licenses": len(all_licenses),
        "active_licenses": active_count,
        "expired_licenses": expired_count,
        "revoked_licenses": revoked_count,
        "trial_licenses": trials_count,
        "total_active_devices": total_active_devices,
        "plans_breakdown": plans_breakdown
    }


def export_sales_report(scope: str = "all", db_path: str = DEFAULT_DB_PATH) -> List[Dict[str, Any]]:
    """Export complete sales & license records for spreadsheet download."""
    licenses = list_all_licenses(db_path=db_path)
    now_month_prefix = datetime.utcnow().strftime("%Y-%m")

    output = []
    for l in licenses:
        if scope == "month" and not (l.get("created_at") or "").startswith(now_month_prefix):
            continue
        if scope == "active" and l.get("computed_status") != "active":
            continue

        output.append({
            "License Key": l.get("license_key"),
            "Plan": l.get("plan"),
            "Price Paid (USD)": f"${float(l.get('price_paid') or 0.0):.2f}",
            "Status": (l.get("computed_status") or "").upper(),
            "Customer Name": l.get("customer_name") or "N/A",
            "Customer WhatsApp / Phone": l.get("customer_phone") or "N/A",
            "Customer Email": l.get("customer_email") or "N/A",
            "Payment Method": l.get("payment_method") or "WhatsApp / Admin",
            "Active Devices": f"{l.get('activations_count', 0)} / {l.get('max_activations', 1)}",
            "Created Date": (l.get("created_at") or "").split("T")[0],
            "Expiration Date": (l.get("expires_at") or "").split("T")[0] if l.get("expires_at") else "LIFETIME",
            "Bound PC Machines": l.get("bound_machines") or "None",
            "Bound HWIDs": l.get("bound_hwids") or "None",
            "Admin Notes": l.get("notes") or ""
        })

    return output


def revoke_license(license_key: str, db_path: str = DEFAULT_DB_PATH) -> bool:
    """Revoke/Terminate a license immediately and remove its active device activations."""
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
