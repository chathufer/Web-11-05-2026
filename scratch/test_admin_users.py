import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "backend"))

from database import (
    init_db,
    authenticate_admin_user,
    create_admin_user,
    reset_admin_password,
    delete_admin_user,
    list_admin_users
)

init_db()

# Test seeded superadmin
admin_auth = authenticate_admin_user("admin", "admin2026!")
assert admin_auth is not None, "Failed to authenticate default admin"
assert admin_auth["role"] == "superadmin"
print("[OK] Default admin auth successful (role: superadmin)")

# Test seeded guest
guest_auth = authenticate_admin_user("guest", "guest123")
assert guest_auth is not None, "Failed to authenticate default guest"
assert guest_auth["role"] == "guest"
print("[OK] Default guest auth successful (role: guest)")

# Test create new admin
ok, msg, new_user = create_admin_user("staff1", "staffpass123", role="admin")
assert ok, msg
assert new_user["username"] == "staff1"
print("[OK] Created new admin user: staff1")

# Test auth new admin
auth_staff = authenticate_admin_user("staff1", "staffpass123")
assert auth_staff is not None
print("[OK] Authenticated new admin user staff1")

# Test reset password
ok, msg = reset_admin_password("staff1", "newstaffpass456")
assert ok, msg
assert authenticate_admin_user("staff1", "staffpass123") is None
assert authenticate_admin_user("staff1", "newstaffpass456") is not None
print("[OK] Reset password for staff1 successful")

# Test list admin users
users = list_admin_users()
assert len(users) >= 3
usernames = [u["username"] for u in users]
assert "admin" in usernames and "guest" in usernames and "staff1" in usernames
print(f"[OK] list_admin_users returned {len(users)} users: {usernames}")

# Test cannot delete primary superadmin
ok, msg = delete_admin_user("admin")
assert not ok
print("[OK] Primary superadmin cannot be deleted")

# Test delete staff1
ok, msg = delete_admin_user("staff1")
assert ok, msg
print("[OK] Deleted staff1 successfully")

print("\nALL ADMIN USER MANAGEMENT DB TESTS PASSED!")
