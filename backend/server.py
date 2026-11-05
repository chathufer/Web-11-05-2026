"""
Production License Server for Media Downloader Pro
Provides secure REST APIs for activation, heartbeat verification, deactivation,
key generation, and an interactive Admin Dashboard.
"""

import os
import sys
from datetime import datetime
from functools import wraps

from flask import Flask, request, jsonify, render_template_string, send_file, redirect

# Add parent directory to sys.path so backend modules import cleanly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from website_html import WEBSITE_HTML

from database import (
    init_db,
    create_license,
    get_license_with_activations,
    activate_license,
    verify_license,
    deactivate_license,
    list_all_licenses,
    revoke_license,
    unrevoke_license,
    delete_license,
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

# Admin Security Key
ADMIN_API_KEY = os.environ.get("ADMIN_API_KEY", "MDP_ADMIN_SECRET_KEY_2026")

# Initialize database on startup
init_db()

PLAN_NAMES = {
    "pro_monthly": "Pro Monthly Subscription",
    "pro_yearly": "Pro Annual Subscription",
    "pro_lifetime": "Pro Lifetime License",
    "pro_custom": "Pro Custom License"
}


def require_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Check header, param, or JSON body
        key = (
            request.headers.get("X-Admin-Key")
            or request.args.get("admin_key")
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


@app.route("/download", methods=["GET"])
def download_installer():
    """Serve the single standalone Windows setup installer or redirect to cloud CDN."""
    direct_url = "https://drive.google.com/file/d/1dvu3fgwbYFIF8ehQAUS74eqmNDyJ0wrN/view?usp=sharing"
    return redirect(direct_url, code=302)


@app.route("/api/v1/checkout", methods=["POST"])
def api_checkout():
    """Storefront checkout / instant license generation endpoint."""
    data = request.get_json(silent=True) or {}
    plan = data.get("plan", "pro_lifetime")
    if plan not in PLAN_CODES:
        plan = "pro_lifetime"

    customer_name = data.get("name", "").strip() or "Valued Customer"
    customer_email = data.get("email", "").strip() or ""
    max_devices = 3 if plan == "pro_lifetime" else (2 if plan == "pro_yearly" else 1)

    key = generate_license_key(plan)
    exp = calculate_expiry(plan)

    create_license(
        license_key=key,
        plan=plan,
        customer_name=customer_name,
        customer_email=customer_email,
        expires_at=exp,
        max_activations=max_devices,
        notes="Downloader Pro Storefront Purchase"
    )

    exp_str = exp.strftime("%Y-%m-%d") if exp else "Lifetime (Never Expires)"

    return jsonify({
        "status": "success",
        "license_key": key,
        "plan": plan,
        "plan_title": PLAN_NAMES.get(plan, "Pro Plan"),
        "customer_name": customer_name,
        "customer_email": customer_email,
        "expires_at": exp_str,
        "max_devices": max_devices,
        "download_url": "/download"
    })


@app.route("/api/v1/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "ok",
        "service": "Downloader Pro License Server",
        "version": "2.2.0",
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

    # Build cryptographically signed license payload
    plan = lic_dict.get("plan", "pro_yearly")
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

    plan = lic_dict.get("plan", "pro_yearly")
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


# ---------------- API ENDPOINTS (ADMIN FACING) ----------------

@app.route("/api/v1/admin/generate", methods=["POST"])
@require_admin
def api_admin_generate():
    """Generate a new license key (Protected by Admin API Key)."""
    data = request.get_json(silent=True) or {}
    plan = data.get("plan", "pro_yearly")
    if plan not in PLAN_CODES:
        plan = "pro_yearly"

    customer_name = data.get("customer_name", "").strip()
    customer_email = data.get("customer_email", "").strip()
    custom_days = data.get("custom_days")
    max_activations = int(data.get("max_activations", 1))
    notes = data.get("notes", "").strip()

    key = generate_license_key(plan)
    expires_at = calculate_expiry(plan, custom_days)

    lic = create_license(
        license_key=key,
        plan=plan,
        customer_name=customer_name,
        customer_email=customer_email,
        expires_at=expires_at,
        max_activations=max_activations,
        notes=notes
    )

    return jsonify({
        "status": "success",
        "message": "License key generated successfully.",
        "data": {
            **lic,
            "plan_title": PLAN_NAMES.get(plan, plan),
            "expires_at_formatted": expires_at.strftime("%Y-%m-%d") if expires_at else "Lifetime (Never)"
        }
    })


@app.route("/api/v1/admin/list", methods=["GET"])
@require_admin
def api_admin_list():
    """List all issued license keys."""
    licenses = list_all_licenses()
    for l in licenses:
        l["plan_title"] = PLAN_NAMES.get(l["plan"], l["plan"])
    return jsonify({
        "status": "success",
        "count": len(licenses),
        "data": licenses
    })


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
    <title>License Server — Media Downloader Pro</title>
    <style>
        :root {
            --bg-body: #0F0F12;
            --bg-card: #18181F;
            --bg-card-subtle: #20202A;
            --border: #2D2D3A;
            --primary: #E50914;
            --primary-hover: #BF0811;
            --accent: #2563EB;
            --success: #10B981;
            --text-main: #F9FAFB;
            --text-muted: #9CA3AF;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background: var(--bg-body); color: var(--text-main); padding: 30px 20px; }
        .container { max-width: 1100px; margin: 0 auto; }
        header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px; padding-bottom: 20px; border-bottom: 1px solid var(--border); }
        h1 { font-size: 24px; font-weight: 700; display: flex; align-items: center; gap: 10px; }
        .badge-pro { background: linear-gradient(135deg, #FF416C, #FF4B2B); padding: 3px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; }
        .grid-stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 25px; }
        .stat-card { background: var(--bg-card); border: 1px solid var(--border); padding: 20px; border-radius: 12px; }
        .stat-title { font-size: 13px; color: var(--text-muted); text-transform: uppercase; font-weight: 600; }
        .stat-val { font-size: 28px; font-weight: 700; margin-top: 5px; color: #fff; }
        .card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px; padding: 24px; margin-bottom: 25px; }
        .card-header { font-size: 18px; font-weight: 600; margin-bottom: 15px; }
        .form-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 15px; }
        label { display: block; font-size: 12px; color: var(--text-muted); margin-bottom: 6px; font-weight: 500; }
        input, select { width: 100%; background: var(--bg-card-subtle); border: 1px solid var(--border); color: #fff; padding: 10px 14px; border-radius: 8px; font-size: 14px; }
        input:focus, select:focus { outline: none; border-color: var(--primary); }
        .btn { background: var(--primary); color: #fff; border: none; padding: 11px 20px; border-radius: 8px; font-weight: 600; cursor: pointer; transition: 0.15s; font-size: 14px; }
        .btn:hover { background: var(--primary-hover); }
        .btn-copy { background: #374151; padding: 5px 10px; font-size: 12px; border-radius: 6px; }
        .btn-revoke { background: #DC2626; padding: 5px 10px; font-size: 12px; border-radius: 6px; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 13px; }
        th, td { padding: 12px 14px; text-align: left; border-bottom: 1px solid var(--border); }
        th { color: var(--text-muted); font-size: 12px; text-transform: uppercase; font-weight: 600; }
        tr:hover { background: rgba(255, 255, 255, 0.02); }
        .key-text { font-family: monospace; font-size: 14px; font-weight: 600; color: #60A5FA; }
        .status-pill { padding: 3px 8px; border-radius: 6px; font-size: 11px; font-weight: 600; display: inline-block; }
        .status-active { background: rgba(16, 185, 129, 0.2); color: #34D399; }
        .status-expired { background: rgba(245, 158, 11, 0.2); color: #FBBF24; }
        .status-revoked { background: rgba(239, 68, 68, 0.2); color: #F87171; }
        .toast { position: fixed; bottom: 20px; right: 20px; background: var(--success); color: #fff; padding: 12px 20px; border-radius: 8px; font-weight: 600; display: none; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Media Downloader Pro <span class="badge-pro">LICENSE SERVER</span></h1>
            <div style="font-size: 13px; color: var(--text-muted);">Admin API Protected</div>
        </header>

        <div class="grid-stats">
            <div class="stat-card">
                <div class="stat-title">Total Licenses</div>
                <div class="stat-val" id="stat-total">-</div>
            </div>
            <div class="stat-card">
                <div class="stat-title">Active Devices</div>
                <div class="stat-val" id="stat-devices" style="color: #34D399;">-</div>
            </div>
            <div class="stat-card">
                <div class="stat-title">Monthly Pro</div>
                <div class="stat-val" id="stat-monthly" style="color: #60A5FA;">-</div>
            </div>
            <div class="stat-card">
                <div class="stat-title">Annual & Lifetime</div>
                <div class="stat-val" id="stat-annual" style="color: #F472B6;">-</div>
            </div>
        </div>

        <div class="card">
            <div class="card-header">Generate New Customer License</div>
            <form id="gen-form">
                <div class="form-row">
                    <div>
                        <label>Subscription Tier</label>
                        <select id="plan-select">
                            <option value="pro_monthly">Pro Monthly (30 Days)</option>
                            <option value="pro_yearly" selected>Pro Annual (365 Days)</option>
                            <option value="pro_lifetime">Pro Lifetime (No Expiry)</option>
                        </select>
                    </div>
                    <div>
                        <label>Customer Name</label>
                        <input type="text" id="cust-name" placeholder="e.g. John Doe" required>
                    </div>
                    <div>
                        <label>Customer Email (Optional)</label>
                        <input type="email" id="cust-email" placeholder="john@example.com">
                    </div>
                    <div>
                        <label>Max Devices (Activations)</label>
                        <select id="max-acts">
                            <option value="1" selected>1 PC</option>
                            <option value="2">2 PCs</option>
                            <option value="5">5 PCs (Family)</option>
                        </select>
                    </div>
                </div>
                <button type="submit" class="btn">⚡ Generate & Issue License Key</button>
            </form>
        </div>

        <div class="card">
            <div class="card-header">Issued License Keys</div>
            <div style="overflow-x: auto;">
                <table>
                    <thead>
                        <tr>
                            <th>License Key</th>
                            <th>Customer</th>
                            <th>Plan</th>
                            <th>Status</th>
                            <th>Devices</th>
                            <th>Expires</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody id="licenses-table-body">
                        <tr><td colspan="7" style="text-align: center; color: var(--text-muted);">Loading licenses...</td></tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <div class="toast" id="toast">Copied to clipboard!</div>

    <script>
        const adminKey = "{{ admin_key }}";

        async function fetchLicenses() {
            try {
                const res = await fetch('/api/v1/admin/list?admin_key=' + encodeURIComponent(adminKey));
                const json = await res.json();
                if (json.status === 'success') {
                    renderTable(json.data);
                }
            } catch (err) {
                console.error(err);
            }
        }

        function renderTable(list) {
            const tbody = document.getElementById('licenses-table-body');
            tbody.innerHTML = '';

            let total = list.length;
            let devices = 0;
            let monthly = 0;
            let annual = 0;

            if (list.length === 0) {
                tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; color: var(--text-muted); padding: 30px;">No licenses issued yet. Generate your first key above!</td></tr>';
            }

            list.forEach(lic => {
                devices += (lic.activations_count || 0);
                if (lic.plan === 'pro_monthly') monthly++;
                if (lic.plan === 'pro_yearly' || lic.plan === 'pro_lifetime') annual++;

                const tr = document.createElement('tr');

                let statusBadge = '<span class="status-pill status-active">ACTIVE</span>';
                if (lic.is_revoked) {
                    statusBadge = '<span class="status-pill status-revoked">REVOKED</span>';
                } else if (lic.expires_at && new Date(lic.expires_at) < new Date()) {
                    statusBadge = '<span class="status-pill status-expired">EXPIRED</span>';
                }

                const expStr = lic.expires_at ? lic.expires_at.split('T')[0] : 'Lifetime';

                tr.innerHTML = `
                    <td><span class="key-text">${lic.license_key}</span></td>
                    <td><strong>${lic.customer_name || 'N/A'}</strong><br><small style="color: var(--text-muted)">${lic.customer_email || ''}</small></td>
                    <td>${lic.plan_title}</td>
                    <td>${statusBadge}</td>
                    <td>${lic.activations_count || 0} / ${lic.max_activations}</td>
                    <td>${expStr}</td>
                    <td>
                        <button class="btn btn-copy" onclick="copyKey('${lic.license_key}')">Copy</button>
                        ${!lic.is_revoked ? `<button class="btn btn-revoke" onclick="revokeKey('${lic.license_key}')">Terminate</button>` : `<button class="btn btn-copy" style="background:#059669;color:#fff" onclick="unrevokeKey('${lic.license_key}')">Restore</button>`}
                        <button class="btn" style="background:#272733;color:#F87171" onclick="deleteKey('${lic.license_key}')">Delete</button>
                    </td>
                `;
                tbody.appendChild(tr);
            });

            document.getElementById('stat-total').innerText = total;
            document.getElementById('stat-devices').innerText = devices;
            document.getElementById('stat-monthly').innerText = monthly;
            document.getElementById('stat-annual').innerText = annual;
        }

        document.getElementById('gen-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const plan = document.getElementById('plan-select').value;
            const customer_name = document.getElementById('cust-name').value;
            const customer_email = document.getElementById('cust-email').value;
            const max_activations = document.getElementById('max-acts').value;

            try {
                const res = await fetch('/api/v1/admin/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'X-Admin-Key': adminKey },
                    body: JSON.stringify({ plan, customer_name, customer_email, max_activations })
                });
                const json = await res.json();
                if (json.status === 'success') {
                    showToast('Generated: ' + json.data.license_key);
                    document.getElementById('cust-name').value = '';
                    document.getElementById('cust-email').value = '';
                    fetchLicenses();
                } else {
                    alert('Error: ' + json.message);
                }
            } catch (err) {
                alert('Network error generating key: ' + err);
            }
        });

        async function revokeKey(key) {
            if (!confirm('Are you sure you want to revoke license ' + key + '? The customer will lose Pro access.')) return;
            try {
                const res = await fetch('/api/v1/admin/revoke', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'X-Admin-Key': adminKey },
                    body: JSON.stringify({ key })
                });
                const json = await res.json();
                if (json.status === 'success') {
                    showToast('License revoked.');
                    fetchLicenses();
                }
            } catch (err) {
                alert('Error: ' + err);
            }
        }

        async function unrevokeKey(key) {
            try {
                const res = await fetch('/api/v1/admin/unrevoke', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'X-Admin-Key': adminKey },
                    body: JSON.stringify({ key })
                });
                const json = await res.json();
                if (json.status === 'success') {
                    showToast('License restored.');
                    fetchLicenses();
                }
            } catch (err) {
                alert('Error: ' + err);
            }
        }

        async function deleteKey(key) {
            if (!confirm('Are you sure you want to PERMANENTLY DELETE license ' + key + '? This cannot be undone.')) return;
            try {
                const res = await fetch('/api/v1/admin/delete', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'X-Admin-Key': adminKey },
                    body: JSON.stringify({ key })
                });
                const json = await res.json();
                if (json.status === 'success') {
                    showToast('License permanently deleted.');
                    fetchLicenses();
                } else {
                    alert('Error: ' + json.message);
                }
            } catch (err) {
                alert('Error: ' + err);
            }
        }

        function copyKey(key) {
            navigator.clipboard.writeText(key).then(() => {
                showToast('Copied: ' + key);
            });
        }

        function showToast(msg) {
            const toast = document.getElementById('toast');
            toast.innerText = msg;
            toast.style.display = 'block';
            setTimeout(() => { toast.style.display = 'none'; }, 2500);
        }

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
    print("=" * 60)
    print("      MEDIA DOWNLOADER PRO — LICENSE SERVER BACKEND")
    print("=" * 60)
    print(f"Server Port:       {port}")
    print(f"Admin Dashboard:   http://localhost:{port}/admin")
    print(f"Admin Secret Key:  {ADMIN_API_KEY}")
    print("=" * 60)
    app.run(host="0.0.0.0", port=port, debug=False)
