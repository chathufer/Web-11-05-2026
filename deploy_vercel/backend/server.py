"""
Production License Server for Media Downloader Pro
Provides secure REST APIs for activation, heartbeat verification, deactivation,
key generation, automated CSV sales data sheet exports, and a full-featured Admin Control Center.
"""

import os
import io
import csv
import sys
import json
from datetime import datetime
from functools import wraps

from flask import Flask, request, jsonify, render_template_string, send_file, redirect, Response

# Add parent directory to sys.path so backend modules import cleanly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from website_html import WEBSITE_HTML

from database import (
    init_db,
    create_license,
    update_license,
    extend_license,
    get_license_with_activations,
    deactivate_device_by_id,
    reset_all_devices,
    lookup_hwid,
    activate_license,
    verify_license,
    deactivate_license,
    list_all_licenses,
    get_sales_analytics,
    export_sales_report,
    revoke_license,
    unrevoke_license,
    delete_license,
    DEFAULT_PLAN_PRICES,
    DEFAULT_DB_PATH
)
from keygen import (
    generate_license_key,
    format_license_key,
    calculate_expiry,
    sign_license_payload,
    PLAN_CODES
)

app = Flask(__name__)

# Admin Security Key (defaults to master secret, can be set via env variable)
ADMIN_API_KEY = os.environ.get("ADMIN_API_KEY", "MDP_ADMIN_SECRET_KEY_2026")

# Official Google Drive installer download link
LATEST_INSTALLER_URL = "https://drive.google.com/file/d/1oDrWH2SAtZK_gET-T9O9Ts0KX3Gcrsnc/view?usp=drive_link"
WHATSAPP_GROUP_URL = "https://chat.whatsapp.com/GwABzhDv3z8CAIXINR1hMG"

# Initialize database on startup
init_db()

PLAN_NAMES = {
    "pro_monthly": "Pro Monthly Pass ($1.99/mo)",
    "pro_yearly": "Annual Pro Pass ($14.99/yr)",
    "pro_lifetime": "Lifetime Master Pass ($24.99)",
    "pro_trial": "Pro 7-Day Free Trial",
    "pro_custom": "Custom Pro License"
}


def require_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        key = (
            request.headers.get("X-Admin-Key")
            or request.args.get("admin_key")
            or request.cookies.get("admin_key")
            or (request.is_json and request.json.get("admin_key"))
        )
        if not key or key != ADMIN_API_KEY:
            return jsonify({"status": "error", "message": "Unauthorized. Invalid Admin API Key."}), 401
        return f(*args, **kwargs)
    return decorated


# ---------------- STOREFRONT & CLIENT FACING ENDPOINTS ----------------

@app.route("/", methods=["GET"])
def storefront():
    """Downloader Pro commercial website & storefront."""
    return render_template_string(WEBSITE_HTML)


@app.route("/api/v1/releases", methods=["GET"])
def api_releases():
    """Return published releases list."""
    rel_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "releases.json")
    if not os.path.exists(rel_file):
        rel_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "releases.json")
    if os.path.exists(rel_file):
        try:
            with open(rel_file, "r", encoding="utf-8") as f:
                return jsonify(json.load(f))
        except Exception:
            pass
    return jsonify([])


@app.route("/download", methods=["GET"])
def download_installer():
    """Serve the single standalone Windows setup installer or redirect to Google Drive CDN."""
    requested_v = request.args.get("v", "").strip().lower()

    rel_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "releases.json")
    if not os.path.exists(rel_file):
        rel_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "releases.json")
    if os.path.exists(rel_file):
        try:
            with open(rel_file, "r", encoding="utf-8") as f:
                releases = json.load(f)
                if requested_v:
                    for r in releases:
                        v_str = r.get("version", "").lower()
                        if v_str == requested_v or v_str.lstrip("v") == requested_v:
                            return redirect(r.get("url", LATEST_INSTALLER_URL), code=302)
                elif releases and isinstance(releases, list):
                    return redirect(releases[0].get("url", LATEST_INSTALLER_URL), code=302)
        except Exception:
            pass

    return redirect(LATEST_INSTALLER_URL, code=302)


@app.route("/api/v1/checkout", methods=["POST", "GET"])
def api_checkout():
    """Disabled public key generation. Customers must contact admins in WhatsApp group to buy."""
    return jsonify({
        "status": "contact_admin",
        "message": "Public license key generation is disabled. Please contact admins in our official WhatsApp group to purchase a plan.",
        "whatsapp_url": WHATSAPP_GROUP_URL
    }), 403


@app.route("/api/v1/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "ok",
        "service": "Downloader Pro License Server",
        "version": "2.3.0",
        "timestamp": datetime.utcnow().isoformat()
    })


@app.route("/api/v1/license/activate", methods=["POST"])
def api_activate():
    """Client activation endpoint."""
    data = request.get_json(silent=True) or {}
    key = data.get("key", "").strip()
    hwid = data.get("hwid", "").strip()
    machine_name = data.get("machine_name", "").strip()

    if not key or not hwid:
        return jsonify({"status": "error", "message": "License key and Hardware ID (HWID) are required."}), 400

    success, message, lic_dict = activate_license(key, hwid, machine_name)

    if not success or not lic_dict:
        return jsonify({"status": "error", "message": message}), 400

    plan = lic_dict.get("plan", "pro_lifetime")
    payload = {
        "license_key": lic_dict["license_key"],
        "plan": plan,
        "plan_title": PLAN_NAMES.get(plan, "Pro Plan"),
        "customer_name": lic_dict.get("customer_name") or "Valued Customer",
        "hwid": hwid,
        "created_at": lic_dict["created_at"],
        "expires_at": lic_dict.get("expires_at") or "",
        "max_activations": lic_dict.get("max_activations", 1),
        "is_pro": 1,
        "timestamp": datetime.utcnow().isoformat()
    }
    payload["signature"] = sign_license_payload(payload)

    return jsonify({
        "status": "success",
        "message": message,
        "data": payload
    })


@app.route("/api/v1/license/verify", methods=["POST"])
def api_verify():
    """Client heartbeat/verification endpoint."""
    data = request.get_json(silent=True) or {}
    key = data.get("key", "").strip()
    hwid = data.get("hwid", "").strip()

    if not key or not hwid:
        return jsonify({"status": "error", "message": "License key and HWID are required."}), 400

    success, message, lic_dict = verify_license(key, hwid)

    if not success or not lic_dict:
        return jsonify({"status": "error", "message": message}), 400

    plan = lic_dict.get("plan", "pro_lifetime")
    payload = {
        "license_key": lic_dict["license_key"],
        "plan": plan,
        "plan_title": PLAN_NAMES.get(plan, "Pro Plan"),
        "customer_name": lic_dict.get("customer_name") or "Valued Customer",
        "hwid": hwid,
        "created_at": lic_dict["created_at"],
        "expires_at": lic_dict.get("expires_at") or "",
        "max_activations": lic_dict.get("max_activations", 1),
        "is_pro": 1,
        "timestamp": datetime.utcnow().isoformat()
    }
    payload["signature"] = sign_license_payload(payload)

    return jsonify({
        "status": "success",
        "message": message,
        "data": payload
    })


@app.route("/api/v1/license/deactivate", methods=["POST"])
def api_deactivate():
    """Client device unbinding / transfer endpoint."""
    data = request.get_json(silent=True) or {}
    key = data.get("key", "").strip()
    hwid = data.get("hwid", "").strip()

    if not key or not hwid:
        return jsonify({"status": "error", "message": "Key and HWID are required."}), 400

    success, message = deactivate_license(key, hwid)
    return jsonify({
        "status": "success" if success else "error",
        "message": message
    }), (200 if success else 400)


@app.route("/api/v1/license/trial", methods=["POST"])
def api_trial():
    """Issue or restore 7-Day Free Trial for a physical machine (1 per HWID)."""
    data = request.get_json(silent=True) or {}
    hwid = data.get("hwid", "").strip()
    machine_name = data.get("machine_name", "").strip() or "PC"

    if not hwid:
        return jsonify({"status": "error", "message": "Hardware ID (HWID) is required."}), 400

    from database import get_connection
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT l.id, l.license_key, l.plan, l.expires_at, l.is_revoked, a.activated_at
        FROM activations a
        JOIN licenses l ON a.license_id = l.id
        WHERE a.hwid = ? AND l.plan = 'pro_trial'
    """, (hwid,))
    row = cursor.fetchone()
    conn.close()

    if row:
        exp_str = row["expires_at"] or ""
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
                "message": "The 7-Day Free Trial has already expired on this computer. Contact admins on WhatsApp to buy a Pro license."
            }), 400

        payload = {
            "license_key": row["license_key"],
            "plan": "pro_trial",
            "plan_title": "Pro 7-Day Trial",
            "customer_name": f"Trial User ({machine_name})",
            "hwid": hwid,
            "created_at": row["activated_at"],
            "expires_at": exp_str,
            "max_activations": 1,
            "is_pro": 1,
            "is_trial": 1,
            "timestamp": datetime.utcnow().isoformat()
        }
        payload["signature"] = sign_license_payload(payload)
        return jsonify({
            "status": "success",
            "message": "Your 7-Day Pro Free Trial is currently active!",
            "data": payload
        })

    trial_key = generate_license_key("pro_trial")
    exp_dt = calculate_expiry("pro_trial")
    exp_str = exp_dt.isoformat() if exp_dt else ""
    now_str = datetime.utcnow().isoformat()

    create_license(
        license_key=trial_key,
        plan="pro_trial",
        customer_name=f"Trial User ({machine_name})",
        customer_email="",
        customer_phone="",
        price_paid=0.0,
        payment_method="Free Promotion",
        expires_at=exp_str,
        max_activations=1,
        notes=f"Auto 7-day trial for {hwid}"
    )
    activate_license(trial_key, hwid, machine_name)

    payload = {
        "license_key": trial_key,
        "plan": "pro_trial",
        "plan_title": "Pro 7-Day Trial",
        "customer_name": f"Trial User ({machine_name})",
        "hwid": hwid,
        "created_at": now_str,
        "expires_at": exp_str,
        "max_activations": 1,
        "is_pro": 1,
        "is_trial": 1,
        "timestamp": now_str
    }
    payload["signature"] = sign_license_payload(payload)

    return jsonify({
        "status": "success",
        "message": "🎉 7-Day Pro Free Trial activated successfully on this computer!",
        "data": payload
    })


# ---------------- API ENDPOINTS (ADMIN CONTROL & SALES MANAGEMENT) ----------------

@app.route("/api/v1/admin/summary", methods=["GET"])
@require_admin
def api_admin_summary():
    """Return sales, revenue, and key analytics for the dashboard."""
    stats = get_sales_analytics()
    return jsonify({"status": "success", "data": stats})


@app.route("/api/v1/admin/list", methods=["GET"])
@require_admin
def api_admin_list():
    """List all issued license keys with search, plan, and status filters."""
    q = request.args.get("q", "").strip()
    plan = request.args.get("plan", "").strip()
    status = request.args.get("status", "").strip()

    licenses = list_all_licenses(search_q=q, plan_filter=plan, status_filter=status)
    for l in licenses:
        l["plan_title"] = PLAN_NAMES.get(l["plan"], l["plan"])
    return jsonify({
        "status": "success",
        "count": len(licenses),
        "data": licenses
    })


@app.route("/api/v1/admin/license_details", methods=["GET"])
@require_admin
def api_admin_license_details():
    """Fetch single license details along with all active machine activations."""
    key = request.args.get("key", "").strip()
    if not key:
        return jsonify({"status": "error", "message": "Key is required."}), 400

    lic = get_license_with_activations(key)
    if not lic:
        return jsonify({"status": "error", "message": "License not found."}), 404

    lic["plan_title"] = PLAN_NAMES.get(lic.get("plan"), lic.get("plan"))
    return jsonify({"status": "success", "data": lic})


@app.route("/api/v1/admin/generate", methods=["POST"])
@require_admin
def api_admin_generate():
    """Generate single or batch customer licenses with sales tracking and WhatsApp delivery formatting."""
    data = request.get_json(silent=True) or {}
    plan = data.get("plan", "pro_lifetime")
    if plan not in PLAN_CODES:
        plan = "pro_lifetime"

    quantity = int(data.get("quantity", 1))
    quantity = max(1, min(quantity, 50))

    customer_name = data.get("customer_name", "").strip()
    customer_phone = data.get("customer_phone", "").strip()
    customer_email = data.get("customer_email", "").strip()
    price_paid = data.get("price_paid")
    payment_method = data.get("payment_method", "WhatsApp Direct").strip()
    custom_days = data.get("custom_days")
    max_activations = int(data.get("max_activations", 3 if plan == "pro_lifetime" else (2 if plan == "pro_yearly" else 1)))
    notes = data.get("notes", "").strip()

    expires_at = calculate_expiry(plan, custom_days)

    generated = []
    for i in range(quantity):
        key = generate_license_key(plan)
        c_name = customer_name if quantity == 1 else (f"{customer_name} ({i+1})" if customer_name else f"Batch License {i+1}")
        lic = create_license(
            license_key=key,
            plan=plan,
            customer_name=c_name,
            customer_email=customer_email,
            customer_phone=customer_phone,
            price_paid=float(price_paid) if (price_paid is not None and str(price_paid).strip() != "") else None,
            payment_method=payment_method,
            expires_at=expires_at,
            max_activations=max_activations,
            notes=notes
        )
        lic["plan_title"] = PLAN_NAMES.get(plan, plan)
        lic["expires_at_formatted"] = expires_at.strftime("%Y-%m-%d") if expires_at else "Lifetime (Never Expires)"
        generated.append(lic)

    return jsonify({
        "status": "success",
        "message": f"Successfully generated {quantity} license key(s).",
        "count": quantity,
        "data": generated[0] if quantity == 1 else generated,
        "keys_list": [k["license_key"] for k in generated]
    })


@app.route("/api/v1/admin/update", methods=["POST"])
@require_admin
def api_admin_update():
    """Update editable fields of an existing license."""
    data = request.get_json(silent=True) or {}
    key = data.get("key", "").strip()
    if not key:
        return jsonify({"status": "error", "message": "License key is required."}), 400

    success = update_license(
        license_key=key,
        plan=data.get("plan"),
        customer_name=data.get("customer_name"),
        customer_email=data.get("customer_email"),
        customer_phone=data.get("customer_phone"),
        expires_at=data.get("expires_at"),
        max_activations=data.get("max_activations"),
        price_paid=data.get("price_paid"),
        payment_method=data.get("payment_method"),
        notes=data.get("notes")
    )

    if success:
        return jsonify({"status": "success", "message": f"License {key} updated successfully."})
    return jsonify({"status": "error", "message": f"License {key} not found or update failed."}), 404


@app.route("/api/v1/admin/extend", methods=["POST"])
@require_admin
def api_admin_extend():
    """Extend expiration of a license by N days or convert to Lifetime."""
    data = request.get_json(silent=True) or {}
    key = data.get("key", "").strip()
    add_days = int(data.get("days", 0))
    make_lifetime = bool(data.get("make_lifetime", False))

    if not key:
        return jsonify({"status": "error", "message": "License key is required."}), 400

    success, msg, new_exp = extend_license(key, add_days=add_days, make_lifetime=make_lifetime)
    if success:
        return jsonify({"status": "success", "message": msg, "new_expiration": new_exp})
    return jsonify({"status": "error", "message": msg}), 404


@app.route("/api/v1/admin/reset_devices", methods=["POST"])
@require_admin
def api_admin_reset_devices():
    """Clear all device activations for a license so customer can reactivate on new PCs."""
    data = request.get_json(silent=True) or {}
    key = data.get("key", "").strip()
    if not key:
        return jsonify({"status": "error", "message": "License key is required."}), 400

    count = reset_all_devices(key)
    return jsonify({"status": "success", "message": f"Cleared {count} device activation slot(s) for key {key}."})


@app.route("/api/v1/admin/deactivate_device", methods=["POST"])
@require_admin
def api_admin_deactivate_device():
    """Unbind a specific device activation by its activation ID."""
    data = request.get_json(silent=True) or {}
    act_id = data.get("activation_id")
    if not act_id:
        return jsonify({"status": "error", "message": "Activation ID is required."}), 400

    success = deactivate_device_by_id(int(act_id))
    if success:
        return jsonify({"status": "success", "message": "Device activation unbind successful."})
    return jsonify({"status": "error", "message": "Device activation not found."}), 404


@app.route("/api/v1/admin/lookup_hwid", methods=["GET"])
@require_admin
def api_admin_lookup_hwid():
    """Search for machine activations and licenses by HWID, machine name, or customer."""
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify({"status": "error", "message": "Search query is required."}), 400

    results = lookup_hwid(q)
    return jsonify({"status": "success", "count": len(results), "data": results})


@app.route("/api/v1/admin/export_csv", methods=["GET"])
@require_admin
def api_admin_export_csv():
    """Export and download a clean CSV sales data sheet directly to browser/Excel."""
    scope = request.args.get("scope", "all").lower()
    data = export_sales_report(scope=scope)

    output = io.StringIO()
    # Write UTF-8 BOM so Microsoft Excel opens accented text and currency correctly
    output.write("\ufeff")

    if data:
        writer = csv.DictWriter(output, fieldnames=list(data[0].keys()))
        writer.writeheader()
        for row in data:
            writer.writerow(row)
    else:
        output.write("No records found for selected export scope.\n")

    csv_bytes = output.getvalue().encode("utf-8")
    today_str = datetime.utcnow().strftime("%Y-%m-%d")
    filename = f"DownloaderPro_Sales_Report_{scope}_{today_str}.csv"

    return Response(
        csv_bytes,
        mimetype="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Cache-Control": "no-cache, no-store, must-revalidate"
        }
    )


@app.route("/api/v1/admin/revoke", methods=["POST"])
@require_admin
def api_admin_revoke():
    """Revoke / Terminate a license key immediately."""
    data = request.get_json(silent=True) or {}
    key = data.get("key", "").strip()
    if not key:
        return jsonify({"status": "error", "message": "Key is required."}), 400

    revoked = revoke_license(key)
    if revoked:
        return jsonify({"status": "success", "message": f"License {key} has been terminated and customer Pro abilities revoked."})
    return jsonify({"status": "error", "message": f"License {key} not found."}), 404


@app.route("/api/v1/admin/unrevoke", methods=["POST"])
@require_admin
def api_admin_unrevoke():
    """Restore a previously terminated license key."""
    data = request.get_json(silent=True) or {}
    key = data.get("key", "").strip()
    if not key:
        return jsonify({"status": "error", "message": "Key is required."}), 400

    restored = unrevoke_license(key)
    if restored:
        return jsonify({"status": "success", "message": f"License {key} restored successfully."})
    return jsonify({"status": "error", "message": f"License {key} not found."}), 404


@app.route("/api/v1/admin/delete", methods=["POST"])
@require_admin
def api_admin_delete():
    """Permanently delete a license key and all its records."""
    data = request.get_json(silent=True) or {}
    key = data.get("key", "").strip()
    if not key:
        return jsonify({"status": "error", "message": "Key is required."}), 400

    deleted = delete_license(key)
    if deleted:
        return jsonify({"status": "success", "message": f"License {key} permanently deleted."})
    return jsonify({"status": "error", "message": f"License {key} not found."}), 404


# ---------------- WEB ADMIN DASHBOARD (GUI) ----------------

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>License & Sales Control Center — Downloader Pro</title>
    <style>
        :root {
            --bg-body: #0a0a0e;
            --bg-card: #121218;
            --bg-card-subtle: #191922;
            --bg-card-hover: #1e1e2b;
            --border: #262635;
            --border-focus: #f5a623;
            --gold: #f5a623;
            --gold-glow: rgba(245, 166, 35, 0.25);
            --emerald: #10b981;
            --sapphire: #3b82f6;
            --ruby: #ef4444;
            --amber: #f59e0b;
            --text-main: #f9fafb;
            --text-muted: #94a3b8;
            --font-mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, sans-serif; }
        body { background: var(--bg-body); color: var(--text-main); min-height: 100vh; padding: 24px 16px 60px 16px; }
        .container { max-width: 1380px; margin: 0 auto; }

        /* Top Header */
        header { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px; margin-bottom: 24px; padding-bottom: 20px; border-bottom: 1px solid var(--border); }
        .brand { display: flex; align-items: center; gap: 12px; }
        .brand-logo { width: 36px; height: 36px; background: linear-gradient(135deg, #f5a623, #ff6b4a); border-radius: 9px; display: flex; align-items: center; justify-content: center; font-weight: 900; color: #0a0a0e; font-size: 18px; box-shadow: 0 4px 14px var(--gold-glow); }
        h1 { font-size: 22px; font-weight: 800; letter-spacing: -0.02em; color: #fff; }
        .badge-live { display: inline-flex; align-items: center; gap: 6px; background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.35); padding: 3px 9px; border-radius: 20px; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; }
        .live-dot { width: 7px; height: 7px; background: #10b981; border-radius: 50%; box-shadow: 0 0 8px #10b981; animation: pulse 2s infinite; }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }

        .header-actions { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
        .btn { display: inline-flex; align-items: center; gap: 7px; background: var(--bg-card-subtle); color: var(--text-main); border: 1px solid var(--border); padding: 9px 16px; border-radius: 8px; font-weight: 600; font-size: 13px; cursor: pointer; transition: all 0.15s ease; text-decoration: none; }
        .btn:hover { background: var(--bg-card-hover); border-color: #3b3b4f; }
        .btn-gold { background: linear-gradient(135deg, #f5a623, #e59512); color: #0a0a0e; border: none; font-weight: 700; box-shadow: 0 3px 12px var(--gold-glow); }
        .btn-gold:hover { background: linear-gradient(135deg, #ffb53f, #f5a623); transform: translateY(-1px); }
        .btn-emerald { background: #059669; color: #fff; border: none; }
        .btn-emerald:hover { background: #047857; }
        .btn-sm { padding: 5px 10px; font-size: 11.5px; border-radius: 6px; }

        /* KPI Analytics Cards */
        .grid-kpis { display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 14px; margin-bottom: 24px; }
        .kpi-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px; padding: 18px 20px; position: relative; overflow: hidden; }
        .kpi-card::before { content: ""; position: absolute; top: 0; left: 0; right: 0; height: 3px; background: var(--accent-bar, var(--border)); }
        .kpi-title { font-size: 12px; font-weight: 700; text-transform: uppercase; color: var(--text-muted); letter-spacing: 0.05em; display: flex; justify-content: space-between; align-items: center; }
        .kpi-val { font-size: 28px; font-weight: 800; margin-top: 6px; color: #fff; letter-spacing: -0.02em; }
        .kpi-sub { font-size: 12px; color: var(--text-muted); margin-top: 4px; display: flex; align-items: center; gap: 4px; }

        /* Tab Navigation */
        .tabs-nav { display: flex; gap: 8px; border-bottom: 1px solid var(--border); margin-bottom: 20px; overflow-x: auto; padding-bottom: 2px; }
        .tab-btn { background: none; border: none; color: var(--text-muted); padding: 10px 18px; font-size: 13.5px; font-weight: 700; cursor: pointer; border-bottom: 2px solid transparent; transition: all 0.15s ease; white-space: nowrap; }
        .tab-btn:hover { color: var(--text-main); }
        .tab-btn.is-active { color: var(--gold); border-bottom-color: var(--gold); }

        .tab-content { display: none; }
        .tab-content.is-active { display: block; }

        /* Cards & Forms */
        .card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px; padding: 22px; margin-bottom: 22px; }
        .card-header { font-size: 16px; font-weight: 700; margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; }
        .card-header h3 { font-size: 16px; font-weight: 700; }
        .form-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; margin-bottom: 16px; }
        .form-group { display: flex; flex-direction: column; }
        label { font-size: 12px; font-weight: 600; color: var(--text-muted); margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.04em; }
        input, select, textarea { width: 100%; background: var(--bg-card-subtle); border: 1.5px solid var(--border); color: #fff; padding: 10px 12px; border-radius: 8px; font-size: 13.5px; transition: border-color 0.15s ease; }
        input:focus, select:focus, textarea:focus { outline: none; border-color: var(--gold); background: var(--bg-card-hover); }

        /* Filters & Search Toolbar */
        .table-toolbar { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; margin-bottom: 16px; }
        .search-box { position: relative; flex: 1; min-width: 260px; max-width: 440px; }
        .search-box input { padding-left: 36px; }
        .search-icon { position: absolute; left: 12px; top: 50%; transform: translateY(-50%); color: var(--text-muted); width: 15px; height: 15px; pointer-events: none; }
        .filter-group { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }

        /* Data Table */
        .table-wrap { overflow-x: auto; border: 1px solid var(--border); border-radius: 10px; background: var(--bg-card); }
        table { width: 100%; border-collapse: collapse; font-size: 13px; text-align: left; }
        th, td { padding: 13px 15px; border-bottom: 1px solid var(--border); vertical-align: middle; }
        th { background: var(--bg-card-subtle); color: var(--text-muted); font-size: 11.5px; text-transform: uppercase; font-weight: 700; letter-spacing: 0.05em; }
        tr:last-child td { border-bottom: none; }
        tr:hover td { background: rgba(255, 255, 255, 0.015); }
        .key-badge { font-family: var(--font-mono); font-size: 13px; font-weight: 700; color: #60a5fa; background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.25); padding: 4px 8px; border-radius: 6px; cursor: pointer; display: inline-flex; align-items: center; gap: 6px; }
        .key-badge:hover { background: rgba(59, 130, 246, 0.2); }

        /* Status & Plan Badges */
        .pill { display: inline-flex; align-items: center; gap: 5px; padding: 3px 8px; border-radius: 6px; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em; }
        .pill-active { background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }
        .pill-expired { background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }
        .pill-revoked { background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }
        .pill-trial { background: rgba(6, 182, 212, 0.15); color: #22d3ee; border: 1px solid rgba(6, 182, 212, 0.3); }

        .plan-tag { font-weight: 700; font-size: 12px; }
        .plan-lft { color: #f5a623; }
        .plan-yea { color: #a78bfa; }
        .plan-mon { color: #60a5fa; }
        .plan-tri { color: #2dd4bf; }

        /* Modals */
        dialog { margin: auto; background: var(--bg-card); color: var(--text-main); border: 1px solid var(--border); border-radius: 14px; max-width: 600px; width: 92%; padding: 0; box-shadow: 0 20px 50px rgba(0, 0, 0, 0.7); }
        dialog::backdrop { background: rgba(0, 0, 0, 0.75); backdrop-filter: blur(4px); }
        .modal-body { padding: 24px; }
        .modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 18px; border-bottom: 1px solid var(--border); padding-bottom: 14px; }
        .modal-header h3 { font-size: 18px; font-weight: 700; }
        .modal-close { background: none; border: none; color: var(--text-muted); font-size: 20px; cursor: pointer; }
        .modal-close:hover { color: #fff; }

        /* Toast */
        .toast { position: fixed; bottom: 24px; right: 24px; background: #059669; color: #fff; padding: 12px 20px; border-radius: 8px; font-weight: 700; font-size: 13.5px; box-shadow: 0 6px 20px rgba(0,0,0,0.5); z-index: 9999; display: none; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="brand">
                <div class="brand-logo">DP</div>
                <div>
                    <h1>Media Downloader Pro <span style="font-size: 14px; font-weight: 500; color: var(--text-muted);">| License Server &amp; Sales Center</span></h1>
                    <div style="margin-top: 4px; display: flex; align-items: center; gap: 8px;">
                        <span class="badge-live"><span class="live-dot"></span> Online Backend API</span>
                        <span style="font-size: 11.5px; color: var(--text-muted);">Authenticated Admin Mode</span>
                    </div>
                </div>
            </div>

            <div class="header-actions">
                <a href="/api/v1/admin/export_csv?scope=all" id="btnExportAllCsv" class="btn btn-emerald" title="Download spreadsheet of all customers and license keys">
                    <span>📊 Download Sales Sheet (.CSV)</span>
                </a>
                <button class="btn btn-gold" onclick="switchTab('tab-generate')">
                    <span>⚡ Issue New Key</span>
                </button>
                <button class="btn" onclick="openKeyModal()" title="View or change current admin authorization key">
                    <span>🔑 Admin Key</span>
                </button>
                <button class="btn" onclick="fetchSummary(); fetchLicenses();" title="Refresh live records">
                    <span>🔄 Refresh</span>
                </button>
            </div>
        </header>

        <!-- KPI Revenue & License Summary Cards -->
        <div class="grid-kpis">
            <div class="kpi-card" style="--accent-bar: #f5a623;">
                <div class="kpi-title">Gross Sales Revenue <span>💰</span></div>
                <div class="kpi-val" id="kpi-total-rev" style="color: #f5a623;">$0.00</div>
                <div class="kpi-sub" id="kpi-month-rev">This Month: $0.00</div>
            </div>
            <div class="kpi-card" style="--accent-bar: #10b981;">
                <div class="kpi-title">Active Pro Licenses <span>🔑</span></div>
                <div class="kpi-val" id="kpi-active-lic" style="color: #34d399;">0</div>
                <div class="kpi-sub" id="kpi-total-lic">Total Issued: 0</div>
            </div>
            <div class="kpi-card" style="--accent-bar: #3b82f6;">
                <div class="kpi-title">Bound Devices (PCs) <span>💻</span></div>
                <div class="kpi-val" id="kpi-devices" style="color: #60a5fa;">0</div>
                <div class="kpi-sub">Physical Machines Active</div>
            </div>
            <div class="kpi-card" style="--accent-bar: #a78bfa;">
                <div class="kpi-title">Tiers Breakdown <span>📦</span></div>
                <div class="kpi-val" style="font-size: 15px; font-weight: 700; margin-top: 10px; line-height: 1.5;" id="kpi-tiers">
                    Lifetime: 0 | Annual: 0<br>Monthly: 0 | Trial: 0
                </div>
            </div>
        </div>

        <!-- Tab Controls -->
        <div class="tabs-nav">
            <button class="tab-btn is-active" onclick="switchTab('tab-licenses')">📋 All Licenses &amp; Control Center</button>
            <button class="tab-btn" onclick="switchTab('tab-generate')">⚡ Generate &amp; Deliver Key</button>
            <button class="tab-btn" onclick="switchTab('tab-sales')">📊 Sales Report &amp; Data Sheet</button>
            <button class="tab-btn" onclick="switchTab('tab-hwid')">🔍 HWID &amp; Device Inspector</button>
        </div>

        <!-- TAB 1: ALL LICENSES TABLE -->
        <div class="tab-content is-active" id="tab-licenses">
            <div class="table-toolbar">
                <div class="search-box">
                    <svg class="search-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
                    <input type="text" id="filter-search" placeholder="Search by Key, Customer Name, Phone, Email, HWID..." oninput="debounceSearch()">
                </div>
                <div class="filter-group">
                    <select id="filter-plan" onchange="fetchLicenses()" style="width: auto; padding: 8px 12px; font-size: 13px;">
                        <option value="all">All Plans</option>
                        <option value="pro_lifetime">Lifetime ($24.99)</option>
                        <option value="pro_yearly">Annual ($14.99)</option>
                        <option value="pro_monthly">Monthly ($1.99)</option>
                        <option value="pro_trial">7-Day Trial</option>
                    </select>
                    <select id="filter-status" onchange="fetchLicenses()" style="width: auto; padding: 8px 12px; font-size: 13px;">
                        <option value="all">All Statuses</option>
                        <option value="active">Active Only</option>
                        <option value="expired">Expired Only</option>
                        <option value="revoked">Revoked Only</option>
                        <option value="trial">Free Trials</option>
                    </select>
                </div>
            </div>

            <div class="table-wrap">
                <table>
                    <thead>
                        <tr>
                            <th>License Key</th>
                            <th>Customer &amp; WhatsApp</th>
                            <th>Plan &amp; Price</th>
                            <th>Status</th>
                            <th>Devices</th>
                            <th>Expires</th>
                            <th>Actions &amp; WhatsApp</th>
                        </tr>
                    </thead>
                    <tbody id="licenses-tbody">
                        <tr><td colspan="7" style="text-align: center; color: var(--text-muted); padding: 40px;">Loading customer licenses...</td></tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- TAB 2: GENERATE & DELIVER KEY -->
        <div class="tab-content" id="tab-generate">
            <div class="card">
                <div class="card-header">
                    <h3>⚡ Issue &amp; Deliver Customer License</h3>
                    <span style="font-size: 12.5px; color: var(--text-muted);">Generate official key and prepare 1-click WhatsApp delivery message</span>
                </div>
                <form id="form-generate" onsubmit="handleGenerateKey(event)">
                    <div class="form-grid">
                        <div class="form-group">
                            <label>Subscription Tier</label>
                            <select id="gen-plan" onchange="updateGenPriceDefault()">
                                <option value="pro_lifetime" selected>Pro Lifetime Master Pass ($24.99)</option>
                                <option value="pro_yearly">Pro Annual Pass ($14.99 / yr)</option>
                                <option value="pro_monthly">Pro Monthly Pass ($1.99 / mo)</option>
                                <option value="pro_trial">7-Day Free Trial ($0.00)</option>
                                <option value="pro_custom">Custom Days Pass</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Quantity to Generate</label>
                            <select id="gen-qty">
                                <option value="1" selected>1 Key (Customer Order)</option>
                                <option value="5">5 Keys (Batch Pre-generate)</option>
                                <option value="10">10 Keys (Batch Pre-generate)</option>
                                <option value="20">20 Keys (Batch Pre-generate)</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Amount Paid (USD $)</label>
                            <input type="number" step="0.01" id="gen-price" value="24.99">
                        </div>
                        <div class="form-group">
                            <label>Payment Method</label>
                            <select id="gen-method">
                                <option value="WhatsApp Direct" selected>WhatsApp Direct / Admin</option>
                                <option value="PayPal">PayPal</option>
                                <option value="Bank Transfer">Bank Transfer</option>
                                <option value="Crypto">Crypto (USDT / BTC)</option>
                                <option value="Card">Credit / Debit Card</option>
                                <option value="Free Promo">Free Promo / Gift</option>
                            </select>
                        </div>
                    </div>

                    <div class="form-grid">
                        <div class="form-group">
                            <label>Customer Name</label>
                            <input type="text" id="gen-name" placeholder="e.g. John Doe">
                        </div>
                        <div class="form-group">
                            <label>Customer WhatsApp / Phone</label>
                            <input type="text" id="gen-phone" placeholder="e.g. +1 555 123 4567 or @username">
                        </div>
                        <div class="form-group">
                            <label>Customer Email (Optional)</label>
                            <input type="email" id="gen-email" placeholder="customer@example.com">
                        </div>
                        <div class="form-group">
                            <label>Max Device Slots</label>
                            <select id="gen-max-acts">
                                <option value="1">1 PC</option>
                                <option value="2">2 PCs</option>
                                <option value="3" selected>3 PCs (Standard)</option>
                                <option value="5">5 PCs (Power User)</option>
                                <option value="10">10 PCs (Enterprise)</option>
                            </select>
                        </div>
                    </div>

                    <div class="form-group" style="margin-bottom: 18px;">
                        <label>Internal Admin Notes (Optional)</label>
                        <input type="text" id="gen-notes" placeholder="e.g. Paid via WhatsApp chat, invoice #402">
                    </div>

                    <button type="submit" class="btn btn-gold" style="padding: 12px 24px; font-size: 14px;">
                        <span>⚡ Generate &amp; Prepare WhatsApp Delivery</span>
                    </button>
                </form>
            </div>
        </div>

        <!-- TAB 3: SALES REPORT & DATA SHEET EXPORTS -->
        <div class="tab-content" id="tab-sales">
            <div class="card">
                <div class="card-header">
                    <div>
                        <h3>📊 Sales Data Sheet &amp; Financial Reports</h3>
                        <p style="font-size: 13px; color: var(--text-muted); margin-top: 4px;">Download complete spreadsheets of sales, customers, dates, and device activations.</p>
                    </div>
                    <div style="display:flex; gap:10px; flex-wrap:wrap;">
                        <a href="/api/v1/admin/export_csv?scope=all" id="btnExportAll2" class="btn btn-emerald">
                            <span>📥 Download All-Time Sales (.CSV)</span>
                        </a>
                        <a href="/api/v1/admin/export_csv?scope=month" id="btnExportMonth" class="btn">
                            <span>📅 Download This Month's Sales (.CSV)</span>
                        </a>
                        <a href="/api/v1/admin/export_csv?scope=active" id="btnExportActive" class="btn">
                            <span>👥 Download Active Pro Users (.CSV)</span>
                        </a>
                    </div>
                </div>

                <div style="margin-top: 20px;">
                    <h4 style="font-size: 14px; text-transform: uppercase; color: var(--text-muted); margin-bottom: 12px;">Sales by Subscription Tier</h4>
                    <div class="table-wrap">
                        <table>
                            <thead>
                                <tr>
                                    <th>Tier / Plan</th>
                                    <th>Standard Price</th>
                                    <th>Licenses Sold</th>
                                    <th>Total Revenue</th>
                                </tr>
                            </thead>
                            <tbody id="sales-breakdown-tbody">
                                <tr><td colspan="4" style="text-align: center; color: var(--text-muted);">Loading revenue breakdown...</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>

        <!-- TAB 4: HWID & DEVICE INSPECTOR -->
        <div class="tab-content" id="tab-hwid">
            <div class="card">
                <div class="card-header">
                    <h3>🔍 Hardware ID &amp; Machine Inspector</h3>
                    <span style="font-size: 12.5px; color: var(--text-muted);">Search any customer's physical machine HWID or PC name</span>
                </div>
                <div style="display: flex; gap: 10px; margin-bottom: 20px; max-width: 600px;">
                    <input type="text" id="hwid-query" placeholder="Enter HWID or Machine Name..." onkeydown="if(event.key==='Enter') searchHwid()">
                    <button class="btn btn-gold" onclick="searchHwid()">Search</button>
                </div>
                <div class="table-wrap">
                    <table>
                        <thead>
                            <tr>
                                <th>Hardware ID (HWID)</th>
                                <th>Machine Name</th>
                                <th>Bound License Key</th>
                                <th>Customer</th>
                                <th>Last Verified</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody id="hwid-results-tbody">
                            <tr><td colspan="6" style="text-align: center; color: var(--text-muted); padding: 30px;">Enter an HWID or machine name above to query.</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <!-- MODAL: WhatsApp Delivery Message Preview -->
    <dialog id="modal-wa">
        <div class="modal-body">
            <div class="modal-header">
                <h3>📱 WhatsApp Customer Delivery Message</h3>
                <button class="modal-close" onclick="document.getElementById('modal-wa').close()">&times;</button>
            </div>
            <p style="font-size: 13px; color: var(--text-muted); margin-bottom: 14px;">
                Copy and paste this ready-to-send message directly to your buyer on WhatsApp:
            </p>
            <textarea id="wa-text-content" rows="12" style="font-family: var(--font-mono); font-size: 12.5px; line-height: 1.45; margin-bottom: 16px;"></textarea>
            <div style="display: flex; gap: 10px; justify-content: flex-end;">
                <button class="btn btn-emerald" onclick="copyWaText()">
                    <span>📋 Copy WhatsApp Message</span>
                </button>
                <button class="btn" onclick="document.getElementById('modal-wa').close()">Close</button>
            </div>
        </div>
    </dialog>

    <!-- MODAL: Manage Devices -->
    <dialog id="modal-devices">
        <div class="modal-body">
            <div class="modal-header">
                <div>
                    <h3 id="dev-modal-title">Active Device Activations</h3>
                    <small id="dev-modal-key" style="color: var(--text-muted); font-family: var(--font-mono);"></small>
                </div>
                <button class="modal-close" onclick="document.getElementById('modal-devices').close()">&times;</button>
            </div>
            <div style="display: flex; justify-content: flex-end; margin-bottom: 14px;">
                <button class="btn btn-sm" style="background:#dc2626; color:#fff;" onclick="resetAllDevicesForCurrentKey()">
                    🔄 Reset All Device Slots
                </button>
            </div>
            <div class="table-wrap">
                <table>
                    <thead>
                        <tr>
                            <th>PC Name</th>
                            <th>Hardware ID (HWID)</th>
                            <th>Activated</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody id="dev-modal-tbody"></tbody>
                </table>
            </div>
        </div>
    </dialog>

    <!-- MODAL: Edit License -->
    <dialog id="modal-edit">
        <div class="modal-body">
            <div class="modal-header">
                <div>
                    <h3>Edit License Details</h3>
                    <small id="edit-modal-key" style="color: var(--text-muted); font-family: var(--font-mono);"></small>
                </div>
                <button class="modal-close" onclick="document.getElementById('modal-edit').close()">&times;</button>
            </div>
            <form onsubmit="handleSaveEdit(event)">
                <input type="hidden" id="edit-key">
                <div class="form-grid">
                    <div class="form-group">
                        <label>Customer Name</label>
                        <input type="text" id="edit-name">
                    </div>
                    <div class="form-group">
                        <label>WhatsApp / Phone</label>
                        <input type="text" id="edit-phone">
                    </div>
                </div>
                <div class="form-grid">
                    <div class="form-group">
                        <label>Customer Email</label>
                        <input type="email" id="edit-email">
                    </div>
                    <div class="form-group">
                        <label>Plan Tier</label>
                        <select id="edit-plan">
                            <option value="pro_lifetime">Lifetime ($24.99)</option>
                            <option value="pro_yearly">Annual ($14.99)</option>
                            <option value="pro_monthly">Monthly ($1.99)</option>
                            <option value="pro_trial">7-Day Trial</option>
                            <option value="pro_custom">Custom</option>
                        </select>
                    </div>
                </div>
                <div class="form-grid">
                    <div class="form-group">
                        <label>Price Paid ($ USD)</label>
                        <input type="number" step="0.01" id="edit-price">
                    </div>
                    <div class="form-group">
                        <label>Max Device Slots</label>
                        <input type="number" id="edit-max-acts" min="1" max="50">
                    </div>
                </div>
                <div class="form-group" style="margin-bottom: 16px;">
                    <label>Admin Notes</label>
                    <input type="text" id="edit-notes">
                </div>
                <div style="display: flex; gap: 10px; justify-content: flex-end;">
                    <button type="submit" class="btn btn-gold">Save Changes</button>
                    <button type="button" class="btn" onclick="document.getElementById('modal-edit').close()">Cancel</button>
                </div>
            </form>
        </div>
    </dialog>

    <!-- MODAL: Admin Key Configuration -->
    <dialog id="modal-key">
        <div class="modal-body">
            <div class="modal-header">
                <h3>Admin Authorization Key</h3>
                <button class="modal-close" onclick="document.getElementById('modal-key').close()">&times;</button>
            </div>
            <p style="font-size: 13px; color: var(--text-muted); margin-bottom: 14px;">
                Enter your secret Admin API Key to access management APIs and download reports:
            </p>
            <div class="form-group" style="margin-bottom: 16px;">
                <label>Admin Secret Key</label>
                <input type="password" id="input-admin-key">
            </div>
            <div style="display: flex; gap: 10px; justify-content: flex-end;">
                <button class="btn btn-gold" onclick="saveAdminKey()">Save &amp; Authenticate</button>
            </div>
        </div>
    </dialog>

    <div class="toast" id="toast">Copied to clipboard!</div>

    <script>
        const DEFAULT_KEY = "{{ admin_key }}";
        let activeAdminKey = localStorage.getItem("mdp_admin_key") || DEFAULT_KEY;
        let currentModalKey = "";
        let searchTimer = null;

        function updateExportLinks() {
            const encoded = encodeURIComponent(activeAdminKey);
            const exp1 = document.getElementById('btnExportAllCsv');
            const exp2 = document.getElementById('btnExportAll2');
            const exp3 = document.getElementById('btnExportMonth');
            const exp4 = document.getElementById('btnExportActive');
            if (exp1) exp1.href = '/api/v1/admin/export_csv?scope=all&admin_key=' + encoded;
            if (exp2) exp2.href = '/api/v1/admin/export_csv?scope=all&admin_key=' + encoded;
            if (exp3) exp3.href = '/api/v1/admin/export_csv?scope=month&admin_key=' + encoded;
            if (exp4) exp4.href = '/api/v1/admin/export_csv?scope=active&admin_key=' + encoded;
            document.cookie = "admin_key=" + encoded + "; path=/; max-age=2592000";
        }

        function switchTab(tabId) {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('is-active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('is-active'));
            const targetBtn = Array.from(document.querySelectorAll('.tab-btn')).find(b => b.getAttribute('onclick').includes(tabId));
            if (targetBtn) targetBtn.classList.add('is-active');
            const targetContent = document.getElementById(tabId);
            if (targetContent) targetContent.classList.add('is-active');
        }

        function updateGenPriceDefault() {
            const plan = document.getElementById('gen-plan').value;
            const priceIn = document.getElementById('gen-price');
            const maxActs = document.getElementById('gen-max-acts');
            if (plan === 'pro_lifetime') { priceIn.value = '24.99'; maxActs.value = '3'; }
            else if (plan === 'pro_yearly') { priceIn.value = '14.99'; maxActs.value = '2'; }
            else if (plan === 'pro_monthly') { priceIn.value = '1.99'; maxActs.value = '1'; }
            else if (plan === 'pro_trial') { priceIn.value = '0.00'; maxActs.value = '1'; }
        }

        async function fetchSummary() {
            try {
                const res = await fetch('/api/v1/admin/summary?admin_key=' + encodeURIComponent(activeAdminKey));
                if (res.status === 401) { openKeyModal(); return; }
                const json = await res.json();
                if (json.status === 'success') {
                    const d = json.data;
                    document.getElementById('kpi-total-rev').innerText = '$' + d.total_revenue.toFixed(2);
                    document.getElementById('kpi-month-rev').innerText = 'This Month: $' + d.month_revenue.toFixed(2);
                    document.getElementById('kpi-active-lic').innerText = d.active_licenses;
                    document.getElementById('kpi-total-lic').innerText = 'Total Issued: ' + d.total_licenses;
                    document.getElementById('kpi-devices').innerText = d.total_active_devices;

                    const p = d.plans_breakdown;
                    document.getElementById('kpi-tiers').innerHTML = `
                        Lifetime: ${p.pro_lifetime.count} ($${p.pro_lifetime.revenue.toFixed(0)}) &middot; Annual: ${p.pro_yearly.count} ($${p.pro_yearly.revenue.toFixed(0)})<br>
                        Monthly: ${p.pro_monthly.count} ($${p.pro_monthly.revenue.toFixed(0)}) &middot; Free Trials: ${p.pro_trial.count}
                    `;

                    renderSalesBreakdown(p);
                }
            } catch (err) {
                console.error(err);
            }
        }

        function renderSalesBreakdown(breakdown) {
            const tbody = document.getElementById('sales-breakdown-tbody');
            tbody.innerHTML = '';
            for (const key in breakdown) {
                const item = breakdown[key];
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><strong>${item.name}</strong></td>
                    <td>${key === 'pro_lifetime' ? '$24.99 one-time' : (key === 'pro_yearly' ? '$14.99 / yr' : (key === 'pro_monthly' ? '$1.99 / mo' : 'Free'))}</td>
                    <td><strong>${item.count}</strong> keys</td>
                    <td style="color:#10b981; font-weight:700;">$${item.revenue.toFixed(2)}</td>
                `;
                tbody.appendChild(tr);
            }
        }

        function debounceSearch() {
            clearTimeout(searchTimer);
            searchTimer = setTimeout(() => { fetchLicenses(); }, 250);
        }

        async function fetchLicenses() {
            const q = document.getElementById('filter-search').value.trim();
            const plan = document.getElementById('filter-plan').value;
            const status = document.getElementById('filter-status').value;

            try {
                const url = `/api/v1/admin/list?admin_key=${encodeURIComponent(activeAdminKey)}&q=${encodeURIComponent(q)}&plan=${encodeURIComponent(plan)}&status=${encodeURIComponent(status)}`;
                const res = await fetch(url);
                if (res.status === 401) { openKeyModal(); return; }
                const json = await res.json();
                if (json.status === 'success') {
                    renderTable(json.data);
                }
            } catch (err) {
                console.error(err);
            }
        }

        function renderTable(list) {
            const tbody = document.getElementById('licenses-tbody');
            tbody.innerHTML = '';

            if (list.length === 0) {
                tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; color: var(--text-muted); padding: 40px;">No licenses match your filter.</td></tr>';
                return;
            }

            list.forEach(lic => {
                const tr = document.createElement('tr');

                let statusBadge = '<span class="pill pill-active">ACTIVE</span>';
                if (lic.computed_status === 'revoked') statusBadge = '<span class="pill pill-revoked">REVOKED</span>';
                else if (lic.computed_status === 'expired') statusBadge = '<span class="pill pill-expired">EXPIRED</span>';
                else if (lic.computed_status === 'trial') statusBadge = '<span class="pill pill-trial">TRIAL</span>';

                let planClass = 'plan-lft';
                if (lic.plan === 'pro_yearly') planClass = 'plan-yea';
                if (lic.plan === 'pro_monthly') planClass = 'plan-mon';
                if (lic.plan === 'pro_trial') planClass = 'plan-tri';

                const expStr = lic.expires_at ? lic.expires_at.split('T')[0] : 'Lifetime';
                const priceStr = '$' + (lic.price_paid || 0).toFixed(2);

                tr.innerHTML = `
                    <td>
                        <span class="key-badge" onclick="copyKey('${lic.license_key}')" title="Click to copy key">
                            ${lic.license_key}
                            <svg width="12" height="12" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path></svg>
                        </span>
                    </td>
                    <td>
                        <strong>${lic.customer_name || 'Valued Customer'}</strong><br>
                        ${lic.customer_phone ? `<small style="color:#25D366; font-weight:600;">📱 ${lic.customer_phone}</small><br>` : ''}
                        <small style="color:var(--text-muted);">${lic.customer_email || ''}</small>
                    </td>
                    <td>
                        <span class="plan-tag ${planClass}">${lic.plan_title}</span><br>
                        <small style="color:var(--text-muted); font-weight:600;">${priceStr} &middot; ${lic.payment_method || 'WhatsApp'}</small>
                    </td>
                    <td>${statusBadge}</td>
                    <td>
                        <button class="btn btn-sm" onclick="openDevicesModal('${lic.license_key}')" title="View bound machines">
                            💻 ${lic.activations_count || 0} / ${lic.max_activations} PCs
                        </button>
                    </td>
                    <td><small style="font-weight:600;">${expStr}</small></td>
                    <td>
                        <div style="display:flex; gap:6px; flex-wrap:wrap;">
                            <button class="btn btn-sm btn-emerald" onclick="openWaModal('${lic.license_key}', '${escapeJs(lic.customer_name)}', '${lic.plan_title}', '${expStr}', ${lic.max_activations})" title="Generate WhatsApp delivery message">
                                📱 Deliver
                            </button>
                            <button class="btn btn-sm" onclick="openEditModal('${lic.license_key}', '${escapeJs(lic.customer_name)}', '${escapeJs(lic.customer_phone)}', '${escapeJs(lic.customer_email)}', '${lic.plan}', ${lic.price_paid || 0}, ${lic.max_activations}, '${escapeJs(lic.notes)}')">
                                ✏️ Edit
                            </button>
                            <button class="btn btn-sm" onclick="extendKeyPrompt('${lic.license_key}')" title="Extend expiration or make lifetime">
                                ⏳ Extend
                            </button>
                            ${!lic.is_revoked ?
                                `<button class="btn btn-sm" style="background:#dc2626; color:#fff;" onclick="revokeKey('${lic.license_key}')">Revoke</button>` :
                                `<button class="btn btn-sm btn-emerald" onclick="unrevokeKey('${lic.license_key}')">Restore</button>`
                            }
                            <button class="btn btn-sm" style="background:#20202a; color:#f87171;" onclick="deleteKey('${lic.license_key}')">🗑️</button>
                        </div>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        }

        function escapeJs(str) {
            return (str || '').replace(/'/g, "\\'").replace(/"/g, '&quot;');
        }

        async function handleGenerateKey(e) {
            e.preventDefault();
            const plan = document.getElementById('gen-plan').value;
            const quantity = parseInt(document.getElementById('gen-qty').value) || 1;
            const price_paid = parseFloat(document.getElementById('gen-price').value) || 0.0;
            const payment_method = document.getElementById('gen-method').value;
            const customer_name = document.getElementById('gen-name').value.trim();
            const customer_phone = document.getElementById('gen-phone').value.trim();
            const customer_email = document.getElementById('gen-email').value.trim();
            const max_activations = parseInt(document.getElementById('gen-max-acts').value) || 3;
            const notes = document.getElementById('gen-notes').value.trim();

            try {
                const res = await fetch('/api/v1/admin/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'X-Admin-Key': activeAdminKey },
                    body: JSON.stringify({
                        plan, quantity, price_paid, payment_method,
                        customer_name, customer_phone, customer_email,
                        max_activations, notes
                    })
                });
                const json = await res.json();
                if (json.status === 'success') {
                    showToast(`Generated ${json.count} license key(s)!`);
                    fetchSummary();
                    fetchLicenses();

                    if (json.count === 1) {
                        const d = json.data;
                        openWaModal(d.license_key, d.customer_name, d.plan_title, d.expires_at_formatted, d.max_activations);
                    } else {
                        const keysStr = json.keys_list.join('\\n');
                        navigator.clipboard.writeText(keysStr);
                        alert(`Successfully generated ${json.count} keys! All keys copied to clipboard:\\n\\n` + keysStr);
                    }
                } else {
                    alert('Error: ' + json.message);
                }
            } catch (err) {
                alert('Network error: ' + err);
            }
        }

        function openWaModal(key, name, planTitle, exp, maxActs) {
            const customerName = name || 'Valued Creator';
            const installerUrl = "https://drive.google.com/file/d/1oDrWH2SAtZK_gET-T9O9Ts0KX3Gcrsnc/view?usp=drive_link";

            const msg = `🎉 *Welcome to Media Downloader Pro VIP!*

Hello ${customerName}, here are your official Pro software license details:

🔑 *License Key:* \`${key}\`
📦 *Plan:* ${planTitle}
💻 *Allowed Devices:* ${maxActs} PC(s)
📅 *Subscription:* ${exp}

⬇️ *Download Latest Windows Setup:*
${installerUrl}

🚀 *Activation Steps:*
1. Run Setup to install Media Downloader Pro on your PC.
2. Launch the application and click the Pro / Key icon (top right).
3. Paste your license key and click "Activate Pro"!

💬 Support: If you ever need help or change your PC, contact us right here in this WhatsApp group!`;

            document.getElementById('wa-text-content').value = msg;
            document.getElementById('modal-wa').showModal();
        }

        function copyWaText() {
            const txt = document.getElementById('wa-text-content').value;
            navigator.clipboard.writeText(txt).then(() => {
                showToast('WhatsApp Delivery Message copied!');
            });
        }

        async function openDevicesModal(key) {
            currentModalKey = key;
            document.getElementById('dev-modal-key').innerText = key;
            const tbody = document.getElementById('dev-modal-tbody');
            tbody.innerHTML = '<tr><td colspan="4" style="text-align:center; padding:20px;">Loading devices...</td></tr>';
            document.getElementById('modal-devices').showModal();

            try {
                const res = await fetch('/api/v1/admin/license_details?key=' + encodeURIComponent(key) + '&admin_key=' + encodeURIComponent(activeAdminKey));
                const json = await res.json();
                if (json.status === 'success') {
                    const acts = json.data.activations || [];
                    if (acts.length === 0) {
                        tbody.innerHTML = '<tr><td colspan="4" style="text-align:center; color:var(--text-muted); padding:30px;">No physical machines have bound this key yet.</td></tr>';
                    } else {
                        tbody.innerHTML = '';
                        acts.forEach(a => {
                            const tr = document.createElement('tr');
                            tr.innerHTML = `
                                <td><strong>${a.machine_name || 'PC'}</strong></td>
                                <td><span style="font-family:var(--font-mono); font-size:12px; color:#60a5fa;">${a.hwid}</span></td>
                                <td><small>${(a.activated_at || '').split('T')[0]}</small></td>
                                <td><button class="btn btn-sm" style="background:#dc2626; color:#fff;" onclick="deactivateDevice(${a.id})">Unbind PC</button></td>
                            `;
                            tbody.appendChild(tr);
                        });
                    }
                }
            } catch (err) {
                tbody.innerHTML = `<tr><td colspan="4" style="color:red; text-align:center;">Failed to load devices: ${err}</td></tr>`;
            }
        }

        async function deactivateDevice(actId) {
            if (!confirm('Unbind this physical PC? The customer will be able to bind a new machine.')) return;
            try {
                const res = await fetch('/api/v1/admin/deactivate_device', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'X-Admin-Key': activeAdminKey },
                    body: JSON.stringify({ activation_id: actId })
                });
                const json = await res.json();
                if (json.status === 'success') {
                    showToast('Device slot unbind successful.');
                    openDevicesModal(currentModalKey);
                    fetchLicenses();
                    fetchSummary();
                } else {
                    alert('Error: ' + json.message);
                }
            } catch (err) {
                alert('Error: ' + err);
            }
        }

        async function resetAllDevicesForCurrentKey() {
            if (!confirm(`Reset ALL device slots for key ${currentModalKey}? All current PCs will need to reactivate.`)) return;
            try {
                const res = await fetch('/api/v1/admin/reset_devices', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'X-Admin-Key': activeAdminKey },
                    body: JSON.stringify({ key: currentModalKey })
                });
                const json = await res.json();
                if (json.status === 'success') {
                    showToast('All device slots cleared.');
                    openDevicesModal(currentModalKey);
                    fetchLicenses();
                    fetchSummary();
                }
            } catch (err) {
                alert('Error: ' + err);
            }
        }

        function openEditModal(key, name, phone, email, plan, price, maxActs, notes) {
            document.getElementById('edit-key').value = key;
            document.getElementById('edit-modal-key').innerText = key;
            document.getElementById('edit-name').value = name || '';
            document.getElementById('edit-phone').value = phone || '';
            document.getElementById('edit-email').value = email || '';
            document.getElementById('edit-plan').value = plan || 'pro_lifetime';
            document.getElementById('edit-price').value = price || 0;
            document.getElementById('edit-max-acts').value = maxActs || 3;
            document.getElementById('edit-notes').value = notes || '';
            document.getElementById('modal-edit').showModal();
        }

        async function handleSaveEdit(e) {
            e.preventDefault();
            const key = document.getElementById('edit-key').value;
            const customer_name = document.getElementById('edit-name').value.trim();
            const customer_phone = document.getElementById('edit-phone').value.trim();
            const customer_email = document.getElementById('edit-email').value.trim();
            const plan = document.getElementById('edit-plan').value;
            const price_paid = parseFloat(document.getElementById('edit-price').value) || 0;
            const max_activations = parseInt(document.getElementById('edit-max-acts').value) || 1;
            const notes = document.getElementById('edit-notes').value.trim();

            try {
                const res = await fetch('/api/v1/admin/update', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'X-Admin-Key': activeAdminKey },
                    body: JSON.stringify({
                        key, customer_name, customer_phone, customer_email,
                        plan, price_paid, max_activations, notes
                    })
                });
                const json = await res.json();
                if (json.status === 'success') {
                    showToast('License updated successfully.');
                    document.getElementById('modal-edit').close();
                    fetchLicenses();
                    fetchSummary();
                } else {
                    alert('Error: ' + json.message);
                }
            } catch (err) {
                alert('Error: ' + err);
            }
        }

        async function extendKeyPrompt(key) {
            const opt = prompt(`Extend License: ${key}\\n\\nEnter:\\n- 30 for +30 Days\\n- 365 for +1 Year\\n- L for Lifetime (Never Expires)`);
            if (!opt) return;

            let days = 0;
            let make_lifetime = false;
            if (opt.trim().toUpperCase() === 'L') {
                make_lifetime = true;
            } else {
                days = parseInt(opt) || 0;
                if (days <= 0) return;
            }

            try {
                const res = await fetch('/api/v1/admin/extend', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'X-Admin-Key': activeAdminKey },
                    body: JSON.stringify({ key, days, make_lifetime })
                });
                const json = await res.json();
                if (json.status === 'success') {
                    showToast(json.message);
                    fetchLicenses();
                } else {
                    alert('Error: ' + json.message);
                }
            } catch (err) {
                alert('Error: ' + err);
            }
        }

        async function revokeKey(key) {
            if (!confirm(`Revoke license ${key}? The customer will immediately lose Pro access.`)) return;
            try {
                const res = await fetch('/api/v1/admin/revoke', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'X-Admin-Key': activeAdminKey },
                    body: JSON.stringify({ key })
                });
                const json = await res.json();
                if (json.status === 'success') {
                    showToast('License terminated.');
                    fetchLicenses();
                    fetchSummary();
                }
            } catch (err) {
                alert('Error: ' + err);
            }
        }

        async function unrevokeKey(key) {
            try {
                const res = await fetch('/api/v1/admin/unrevoke', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'X-Admin-Key': activeAdminKey },
                    body: JSON.stringify({ key })
                });
                const json = await res.json();
                if (json.status === 'success') {
                    showToast('License restored.');
                    fetchLicenses();
                    fetchSummary();
                }
            } catch (err) {
                alert('Error: ' + err);
            }
        }

        async function deleteKey(key) {
            if (!confirm(`PERMANENTLY DELETE license ${key} and all its device history? This cannot be undone.`)) return;
            try {
                const res = await fetch('/api/v1/admin/delete', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'X-Admin-Key': activeAdminKey },
                    body: JSON.stringify({ key })
                });
                const json = await res.json();
                if (json.status === 'success') {
                    showToast('License permanently deleted.');
                    fetchLicenses();
                    fetchSummary();
                }
            } catch (err) {
                alert('Error: ' + err);
            }
        }

        async function searchHwid() {
            const q = document.getElementById('hwid-query').value.trim();
            if (!q) return;
            const tbody = document.getElementById('hwid-results-tbody');
            tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; padding:20px;">Searching database...</td></tr>';

            try {
                const res = await fetch(`/api/v1/admin/lookup_hwid?q=${encodeURIComponent(q)}&admin_key=${encodeURIComponent(activeAdminKey)}`);
                const json = await res.json();
                if (json.status === 'success') {
                    const list = json.data || [];
                    if (list.length === 0) {
                        tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; color:var(--text-muted); padding:30px;">No machine or license matches that search query.</td></tr>';
                    } else {
                        tbody.innerHTML = '';
                        list.forEach(r => {
                            const tr = document.createElement('tr');
                            tr.innerHTML = `
                                <td><span style="font-family:var(--font-mono); font-size:12px; color:#60a5fa;">${r.hwid}</span></td>
                                <td><strong>${r.machine_name || 'PC'}</strong></td>
                                <td><span class="key-badge" onclick="copyKey('${r.license_key}')">${r.license_key}</span></td>
                                <td>${r.customer_name || 'N/A'}</td>
                                <td><small>${(r.last_verified_at || '').split('T')[0]}</small></td>
                                <td><button class="btn btn-sm" style="background:#dc2626; color:#fff;" onclick="deactivateDevice(${r.activation_id})">Unbind</button></td>
                            `;
                            tbody.appendChild(tr);
                        });
                    }
                }
            } catch (err) {
                tbody.innerHTML = `<tr><td colspan="6" style="color:red; text-align:center;">Query failed: ${err}</td></tr>`;
            }
        }

        function openKeyModal() {
            document.getElementById('input-admin-key').value = activeAdminKey;
            document.getElementById('modal-key').showModal();
        }

        function saveAdminKey() {
            const val = document.getElementById('input-admin-key').value.trim();
            if (val) {
                activeAdminKey = val;
                localStorage.setItem("mdp_admin_key", val);
                updateExportLinks();
                document.getElementById('modal-key').close();
                showToast('Admin key saved.');
                fetchSummary();
                fetchLicenses();
            }
        }

        function copyKey(k) {
            navigator.clipboard.writeText(k).then(() => {
                showToast('Copied: ' + k);
            });
        }

        function showToast(msg) {
            const t = document.getElementById('toast');
            t.innerText = msg;
            t.style.display = 'block';
            setTimeout(() => { t.style.display = 'none'; }, 2600);
        }

        // Initialize dashboard
        updateExportLinks();
        fetchSummary();
        fetchLicenses();
    </script>
</body>
</html>
"""


@app.route("/admin", methods=["GET"])
def admin_dashboard():
    """Web Admin Dashboard route."""
    key = request.args.get("key") or request.cookies.get("admin_key") or ADMIN_API_KEY
    return render_template_string(DASHBOARD_HTML, admin_key=key)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print("=" * 64)
    print("     MEDIA DOWNLOADER PRO — MASTER LICENSE & SALES BACKEND")
    print("=" * 64)
    print(f"Server Port:       {port}")
    print(f"Admin Dashboard:   http://localhost:{port}/admin")
    print(f"Admin Secret Key:  {ADMIN_API_KEY}")
    print(f"Download Setup:    {LATEST_INSTALLER_URL}")
    print(f"VIP WhatsApp:      {WHATSAPP_GROUP_URL}")
    print("=" * 64)
    app.run(host="0.0.0.0", port=port, debug=False)
