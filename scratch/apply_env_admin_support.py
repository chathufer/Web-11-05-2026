# -*- coding: utf-8 -*-
"""
Add environment variable fallback support (ADMIN_USERNAME, ADMIN_PASSWORD, ADMIN_USERS)
so admin credentials persist on Vercel serverless deployments without getting lost on cold starts.
"""
import os
import shutil

print("[1] Updating backend/database.py...")

with open("backend/database.py", "r", encoding="utf-8") as f:
    code = f.read()

# Replace authenticate_admin_user
old_auth = """def authenticate_admin_user(
    username: str,
    password: str,
    db_path: str = DEFAULT_DB_PATH
) -> Optional[Dict[str, Any]]:
    \"\"\"Validate credentials and return user profile if correct.\"\"\"
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM admin_users WHERE username = ?", (username.strip().lower(),))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return None

    user = dict(row)
    if not verify_password(user["password_hash"], password):
        conn.close()
        return None

    now_iso = datetime.utcnow().isoformat()
    cursor.execute("UPDATE admin_users SET last_login = ? WHERE id = ?", (now_iso, user["id"]))
    conn.commit()
    conn.close()

    return {
        "id": user["id"],
        "username": user["username"],
        "role": user["role"],
        "created_at": user["created_at"],
        "last_login": now_iso
    }"""

new_auth = """def authenticate_admin_user(
    username: str,
    password: str,
    db_path: str = DEFAULT_DB_PATH
) -> Optional[Dict[str, Any]]:
    \"\"\"Validate credentials and return user profile if correct (supports DB + Vercel Env Vars).\"\"\"
    clean_u = (username or "").strip().lower()
    clean_p = (password or "").strip()
    if not clean_u or not clean_p:
        return None

    now_iso = datetime.utcnow().isoformat()

    # 1. Check Vercel / System Environment Variables for 100% persistent cloud login
    env_admin_u = os.environ.get("ADMIN_USERNAME", "").strip().lower()
    env_admin_p = os.environ.get("ADMIN_PASSWORD", "").strip()
    if env_admin_u and clean_u == env_admin_u and clean_p == env_admin_p:
        return {
            "id": 1000,
            "username": clean_u,
            "role": "superadmin",
            "created_at": now_iso,
            "last_login": now_iso
        }

    env_users = os.environ.get("ADMIN_USERS", "")
    if env_users:
        for entry in env_users.split(","):
            parts = [p.strip() for p in entry.split(":") if p.strip()]
            if len(parts) >= 2:
                eu_name = parts[0].lower()
                eu_pass = parts[1]
                eu_role = parts[2].lower() if len(parts) >= 3 else "admin"
                if clean_u == eu_name and clean_p == eu_pass:
                    return {
                        "id": 1001 + (abs(hash(eu_name)) % 500),
                        "username": eu_name,
                        "role": eu_role,
                        "created_at": now_iso,
                        "last_login": now_iso
                    }

    # 2. Check SQLite Database
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM admin_users WHERE username = ?", (clean_u,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return None

    user = dict(row)
    if not verify_password(user["password_hash"], clean_p):
        conn.close()
        return None

    cursor.execute("UPDATE admin_users SET last_login = ? WHERE id = ?", (now_iso, user["id"]))
    conn.commit()
    conn.close()

    return {
        "id": user["id"],
        "username": user["username"],
        "role": user["role"],
        "created_at": user["created_at"],
        "last_login": now_iso
    }"""

code = code.replace(old_auth.replace("\r\n", "\n"), new_auth)

# Replace list_admin_users
old_list = """def list_admin_users(db_path: str = DEFAULT_DB_PATH) -> List[Dict[str, Any]]:
    \"\"\"Fetch list of all administrators and guest users.\"\"\"
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, role, created_at, last_login FROM admin_users ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]"""

new_list = """def list_admin_users(db_path: str = DEFAULT_DB_PATH) -> List[Dict[str, Any]]:
    \"\"\"Fetch list of all administrators (merging DB records with persistent Vercel Env Vars).\"\"\"
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, role, created_at, last_login FROM admin_users ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()
    users = [dict(r) for r in rows]
    usernames = {u["username"].lower() for u in users}

    # Include any admins defined via environment variables
    env_admin_u = os.environ.get("ADMIN_USERNAME", "").strip().lower()
    if env_admin_u and env_admin_u not in usernames:
        users.append({
            "id": 1000,
            "username": env_admin_u,
            "role": "superadmin",
            "created_at": "Vercel Environment Variable",
            "last_login": None
        })
        usernames.add(env_admin_u)

    env_users = os.environ.get("ADMIN_USERS", "")
    if env_users:
        for idx, entry in enumerate(env_users.split(",")):
            parts = [p.strip() for p in entry.split(":") if p.strip()]
            if len(parts) >= 2:
                eu_name = parts[0].lower()
                eu_role = parts[2].lower() if len(parts) >= 3 else "admin"
                if eu_name not in usernames:
                    users.append({
                        "id": 1001 + idx,
                        "username": eu_name,
                        "role": eu_role,
                        "created_at": "Vercel Environment Variable",
                        "last_login": None
                    })
                    usernames.add(eu_name)

    return users"""

code = code.replace(old_list.replace("\r\n", "\n"), new_list)

with open("backend/database.py", "w", encoding="utf-8") as f:
    f.write(code)

with open("deploy_vercel/backend/database.py", "w", encoding="utf-8") as f:
    f.write(code)

print("  [OK] Updated database.py and deploy_vercel/backend/database.py")

# Add persistent notice to backend/server.py
with open("backend/server.py", "r", encoding="utf-8") as f:
    server_code = f.read()

target_marker = '<div class="admin-grid" style="display: grid; grid-template-columns: 1fr 1fr; gap: 24px;">'

notice_box = """<div style="background: rgba(245, 158, 11, 0.08); border: 1.5px solid rgba(245, 158, 11, 0.3); border-radius: 10px; padding: 14px 18px; margin-bottom: 20px; font-size: 12.5px; color: var(--text); line-height: 1.55;">
                <strong style="color: #fbbf24; font-size: 13.5px; display: block; margin-bottom: 4px;">⚡ Permanent Persistence on Vercel Cloud:</strong>
                Vercel Serverless Functions use an ephemeral temporary filesystem. To guarantee custom admin accounts persist 100% across all serverless restarts, you can configure them in your <strong>Vercel Project Settings ➜ Environment Variables</strong> (e.g. <code>ADMIN_USERNAME</code> &amp; <code>ADMIN_PASSWORD</code>), or ask your assistant to commit them directly to the repository database!
            </div>
            <div class="admin-grid" style="display: grid; grid-template-columns: 1fr 1fr; gap: 24px;">"""

if target_marker in server_code:
    server_code = server_code.replace(target_marker, notice_box, 1)

with open("backend/server.py", "w", encoding="utf-8") as f:
    f.write(server_code)

with open("deploy_vercel/backend/server.py", "w", encoding="utf-8") as f:
    f.write(server_code)

print("  [OK] Updated server.py and deploy_vercel/backend/server.py")
