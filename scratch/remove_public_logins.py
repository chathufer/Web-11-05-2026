# -*- coding: utf-8 -*-
"""
Remove all public display of admin credentials, default accounts, guest login buttons,
and the public footer admin portal link.
"""
import os
import sys
import shutil

print("[1] Removing credentials display and quick login from backend/server.py and deploy_vercel/backend/server.py...")

server_files = ["backend/server.py", "deploy_vercel/backend/server.py"]

for sf in server_files:
    if os.path.isfile(sf):
        with open(sf, "r", encoding="utf-8") as f:
            code = f.read()

        # Update input placeholder
        code = code.replace(
            '<input type="text" id="login-username" placeholder="admin or guest" required autocomplete="username">',
            '<input type="text" id="login-username" placeholder="Enter username" required autocomplete="username">'
        )

        # Remove the OR divider, Quick Guest Login button, and Default Accounts info box
        old_login_extras = """            <div style="text-align: center; margin: 18px 0; color: var(--text-muted); font-size: 12px; font-weight: 700;">
                ── OR ──
            </div>

            <button type="button" class="btn btn-cyan" onclick="quickGuestLogin()" style="width: 100%; justify-content: center; padding: 11px; font-size: 13.5px;">
                <span>👁️ Quick Guest Login (Read-Only Demo)</span>
            </button>

            <div style="margin-top: 24px; padding: 12px 14px; background: var(--bg-card-subtle); border-radius: 8px; border: 1px solid var(--border); font-size: 11.5px; color: var(--text-muted); line-height: 1.5;">
                <strong>Default Accounts:</strong><br>
                &bull; Master Admin: <code style="color:#60a5fa;">admin</code> / <code style="color:#60a5fa;">admin2026!</code> (Full Control)<br>
                &bull; Guest Access: <code style="color:#22d3ee;">guest</code> / <code style="color:#22d3ee;">guest123</code> (Read-Only)
            </div>"""

        if old_login_extras in code:
            code = code.replace(old_login_extras, "")
            print(f"  [OK] Removed public credentials and guest button from {sf}")
        else:
            # Check with normalized line endings
            norm_code = code.replace("\r\n", "\n")
            norm_extras = old_login_extras.replace("\r\n", "\n")
            if norm_extras in norm_code:
                code = norm_code.replace(norm_extras, "")
                print(f"  [OK] Removed public credentials and guest button from {sf} (normalized)")

        # Remove quickGuestLogin JS function
        old_quick_func = """        function quickGuestLogin() {
            document.getElementById('login-username').value = 'guest';
            document.getElementById('login-password').value = 'guest123';
            const fakeEvent = { preventDefault: () => {} };
            handleLoginSubmit(fakeEvent);
        }"""
        code = code.replace(old_quick_func, "")
        code = code.replace(old_quick_func.replace("\r\n", "\n"), "")

        # Remove console print of passwords
        code = code.replace('    print("Default Superadmin: admin / admin2026!")\n', '')
        code = code.replace('    print("Default Guest:      guest / guest123")\n', '')

        with open(sf, "w", encoding="utf-8") as f:
            f.write(code)
        print(f"  [OK] Saved {sf}")

print("[2] Removing License Admin Portal link from public website footers...")

html_files = [
    "index.html",
    "public/index.html",
    "deploy_vercel/index.html",
    "deploy_vercel/public/index.html"
]

target_footer_link = '        <a href="/admin">License Admin Portal</a>\n'

for hf in html_files:
    if os.path.isfile(hf):
        with open(hf, "r", encoding="utf-8") as f:
            html = f.read()
        html = html.replace(target_footer_link, "")
        html = html.replace(target_footer_link.replace("\n", "\r\n"), "")
        with open(hf, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"  [OK] Removed admin link from {hf}")

py_html_files = [
    "backend/website_html.py",
    "deploy_vercel/backend/website_html.py"
]

for pf in py_html_files:
    if os.path.isfile(pf):
        with open(pf, "r", encoding="utf-8") as f:
            py_code = f.read()
        py_code = py_code.replace(target_footer_link, "")
        py_code = py_code.replace(target_footer_link.replace("\n", "\r\n"), "")
        with open(pf, "w", encoding="utf-8") as f:
            f.write(py_code)
        print(f"  [OK] Removed admin link from {pf}")

print("[3] Removing default guest account from databases and init_db...")
db_files = ["backend/database.py", "deploy_vercel/backend/database.py"]
for df in db_files:
    if os.path.isfile(df):
        with open(df, "r", encoding="utf-8") as f:
            db_code = f.read()
        
        old_seed = """    # Seed default superadmin ('admin' / 'admin2026!') and guest ('guest' / 'guest123')
    cursor.execute("SELECT COUNT(*) FROM admin_users")
    if cursor.fetchone()[0] == 0:
        now_iso = datetime.utcnow().isoformat()
        admin_pw = hash_password("admin2026!")
        guest_pw = hash_password("guest123")
        cursor.execute(\"\"\"
            INSERT INTO admin_users (username, password_hash, role, created_at)
            VALUES ('admin', ?, 'superadmin', ?)
        \"\"\", (admin_pw, now_iso))
        cursor.execute(\"\"\"
            INSERT INTO admin_users (username, password_hash, role, created_at)
            VALUES ('guest', ?, 'guest', ?)
        \"\"\", (guest_pw, now_iso))"""

        new_seed = """    # Seed default superadmin ('admin') if table is empty
    cursor.execute("SELECT COUNT(*) FROM admin_users")
    if cursor.fetchone()[0] == 0:
        now_iso = datetime.utcnow().isoformat()
        admin_pw = hash_password("admin2026!")
        cursor.execute(\"\"\"
            INSERT INTO admin_users (username, password_hash, role, created_at)
            VALUES ('admin', ?, 'superadmin', ?)
        \"\"\", (admin_pw, now_iso))"""

        if old_seed in db_code:
            db_code = db_code.replace(old_seed, new_seed)
        else:
            db_code = db_code.replace(old_seed.replace("\r\n", "\n"), new_seed.replace("\r\n", "\n"))

        with open(df, "w", encoding="utf-8") as f:
            f.write(db_code)
        print(f"  [OK] Updated init_db seed in {df}")

# Delete guest account from sqlite databases
import sqlite3
for db_path in ["backend/licenses.db", "deploy_vercel/backend/licenses.db"]:
    if os.path.isfile(db_path):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("DELETE FROM admin_users WHERE username = 'guest'")
        conn.commit()
        c.execute("SELECT username, role FROM admin_users")
        remaining = c.fetchall()
        conn.close()
        print(f"  [OK] Cleaned admin_users in {db_path}: remaining = {remaining}")

print("\nALL PUBLIC CREDENTIALS, GUEST SHORTCUTS & FOOTER ADMIN LINKS REMOVED!")
