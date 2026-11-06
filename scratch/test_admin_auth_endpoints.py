import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "backend"))

from database import init_db
from server import app, ADMIN_API_KEY

print("Testing Admin & Guest Authentication, Permissions, and User Management Endpoints...")

init_db()
client = app.test_client()

# 1. Login with wrong credentials (expect 401)
res = client.post("/api/v1/admin/login", json={"username": "admin", "password": "wrongpassword"})
assert res.status_code == 401, f"Expected 401 for wrong pw, got {res.status_code}"
print("[OK] Invalid credentials correctly rejected (401)")

# 2. Login as Superadmin ('admin' / 'admin2026!')
res = client.post("/api/v1/admin/login", json={"username": "admin", "password": "admin2026!"})
assert res.status_code == 200, f"Expected 200, got {res.status_code}"
admin_data = res.get_json()
assert admin_data["status"] == "success"
assert admin_data["user"]["role"] == "superadmin"
admin_token = admin_data["token"]
print("[OK] Superadmin login successful (role: superadmin)")

# 2b. Verify default guest no longer exists for public secrecy
res = client.post("/api/v1/admin/login", json={"username": "guest", "password": "guest123"})
assert res.status_code == 401, "Public default guest account must NOT exist"
print("[OK] Default guest account correctly absent (confidential logins)")

# 3. Create a Guest account for role-permission testing
res = client.post("/api/v1/admin/users/create", headers={"Authorization": f"Bearer {admin_token}"}, json={
    "username": "guest_role_tester",
    "password": "guest_secret_pass",
    "role": "guest"
})
assert res.status_code == 200

res = client.post("/api/v1/admin/login", json={"username": "guest_role_tester", "password": "guest_secret_pass"})
assert res.status_code == 200, f"Expected 200, got {res.status_code}"
guest_data = res.get_json()
assert guest_data["status"] == "success"
assert guest_data["user"]["role"] == "guest"
guest_token = guest_data["token"]
print("[OK] Created guest user logged in successfully (role: guest)")

# 4. Test Guest Read-Only Permissions
# 4a. Guest CAN read summary (GET)
res = client.get("/api/v1/admin/summary", headers={"Authorization": f"Bearer {guest_token}"})
assert res.status_code == 200, f"Guest should be able to read summary, got {res.status_code}"
print("[OK] Guest read-only access to summary permitted (200)")

# 4b. Guest CANNOT generate key (POST) -> 403 Forbidden
res = client.post("/api/v1/admin/generate", headers={"Authorization": f"Bearer {guest_token}"}, json={"plan": "pro_yearly"})
assert res.status_code == 403, f"Guest should be blocked from generating keys, got {res.status_code}"
print("[OK] Guest mutation attempt correctly blocked (403 Forbidden)")

# 4c. Guest CANNOT access admin user management -> 403 Forbidden
res = client.get("/api/v1/admin/users/list", headers={"Authorization": f"Bearer {guest_token}"})
assert res.status_code == 403, f"Guest should be blocked from admin user list, got {res.status_code}"
print("[OK] Guest access to admin accounts correctly blocked (403 Forbidden)")

# 5. Test Admin User Management Endpoints (as admin)
# 5a. List admin users
res = client.get("/api/v1/admin/users/list", headers={"Authorization": f"Bearer {admin_token}"})
assert res.status_code == 200
users = res.get_json()["data"]
usernames = [u["username"] for u in users]
assert "admin" in usernames
print(f"[OK] GET /api/v1/admin/users/list returned {len(users)} users: {usernames}")

# 5b. Create new admin account
res = client.post("/api/v1/admin/users/create", headers={"Authorization": f"Bearer {admin_token}"}, json={
    "username": "moderator_test",
    "password": "initialpassword123",
    "role": "admin"
})
assert res.status_code == 200, f"Failed to create new admin: {res.get_json()}"
print("[OK] POST /api/v1/admin/users/create created user 'moderator_test'")

# 5c. Login as newly created admin
res = client.post("/api/v1/admin/login", json={"username": "moderator_test", "password": "initialpassword123"})
assert res.status_code == 200
mod_token = res.get_json()["token"]
print("[OK] Newly created admin 'moderator_test' logged in successfully")

# 5d. Reset password for newly created admin
res = client.post("/api/v1/admin/users/reset_password", headers={"Authorization": f"Bearer {admin_token}"}, json={
    "username": "moderator_test",
    "new_password": "updatedpassword456"
})
assert res.status_code == 200
print("[OK] POST /api/v1/admin/users/reset_password updated password for 'moderator_test'")

# 5e. Old password fails, new password succeeds
res = client.post("/api/v1/admin/login", json={"username": "moderator_test", "password": "initialpassword123"})
assert res.status_code == 401
res = client.post("/api/v1/admin/login", json={"username": "moderator_test", "password": "updatedpassword456"})
assert res.status_code == 200
print("[OK] New password verified for 'moderator_test'")

# 5f. Delete moderator_test
res = client.post("/api/v1/admin/users/delete", headers={"Authorization": f"Bearer {admin_token}"}, json={
    "username": "moderator_test"
})
assert res.status_code == 200
client.post("/api/v1/admin/users/delete", headers={"Authorization": f"Bearer {admin_token}"}, json={"username": "guest_role_tester"})
print("[OK] Cleaned up temporary test users")

# 6. Verify legacy ADMIN_API_KEY backwards compatibility
res = client.get(f"/api/v1/admin/summary?admin_key={ADMIN_API_KEY}")
assert res.status_code == 200
print("[OK] Legacy ADMIN_API_KEY authentication continues to work seamlessly")

print("\nALL ADMIN AUTHENTICATION, GUEST & USER MANAGEMENT TESTS PASSED PERFECTLY!")
