import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "backend"))

from database import (
    init_db,
    create_license,
    update_license,
    extend_license,
    activate_license,
    lookup_hwid,
    get_sales_analytics,
    export_sales_report,
    reset_all_devices,
    deactivate_device_by_id,
    revoke_license,
    unrevoke_license,
    delete_license
)
from server import app, ADMIN_API_KEY

print("Testing License Manager & Sales Backend...")

# 1. Initialize DB
init_db()

delete_license("MDP-LFT-TEST-1234-ABCD")

# 2. Test create_license with sales fields
lic = create_license(
    license_key="MDP-LFT-TEST-1234-ABCD",
    plan="pro_lifetime",
    customer_name="John Doe",
    customer_email="john@example.com",
    customer_phone="+1234567890",
    price_paid=24.99,
    payment_method="WhatsApp Direct",
    notes="Test order"
)
assert lic["customer_phone"] == "+1234567890"
assert lic["price_paid"] == 24.99
print("[OK] create_license with price_paid and customer_phone successful")

# 3. Test device activation & HWID lookup
success, msg, _ = activate_license("MDP-LFT-TEST-1234-ABCD", "HWID-TEST-PC-9999", "Johns-Gaming-PC")
assert success, msg
results = lookup_hwid("HWID-TEST-PC-9999")
assert len(results) > 0
assert results[0]["machine_name"] == "Johns-Gaming-PC"
print("[OK] activate_license and lookup_hwid successful")

# 4. Test update_license
ok = update_license("MDP-LFT-TEST-1234-ABCD", customer_name="Johnathan Doe", price_paid=25.00)
assert ok
print("[OK] update_license successful")

# 5. Test extend_license
ok, msg, new_exp = extend_license("MDP-LFT-TEST-1234-ABCD", make_lifetime=True)
assert ok
print("[OK] extend_license (make_lifetime) successful")

# 6. Test get_sales_analytics
analytics = get_sales_analytics()
assert "total_revenue" in analytics
assert analytics["total_revenue"] > 0
print(f"[OK] get_sales_analytics: Total Revenue = ${analytics['total_revenue']}, Active Licenses = {analytics['active_licenses']}")

# 7. Test export_sales_report
rows = export_sales_report()
assert len(rows) > 0
assert "License Key" in rows[0]
assert "Price Paid (USD)" in rows[0]
assert "Customer WhatsApp / Phone" in rows[0]
print(f"[OK] export_sales_report: Exported {len(rows)} records with CSV columns")

# 8. Test Flask test client for API endpoints
client = app.test_client()

# Summary API
resp = client.get(f"/api/v1/admin/summary?admin_key={ADMIN_API_KEY}")
assert resp.status_code == 200
data = resp.get_json()
assert data["status"] == "success"
print("[OK] GET /api/v1/admin/summary successful")

# Batch generation
resp = client.post("/api/v1/admin/generate", json={
    "admin_key": ADMIN_API_KEY,
    "plan": "pro_yearly",
    "quantity": 3,
    "customer_name": "VIP Customer",
    "customer_phone": "+987654321",
    "price_paid": 14.99,
    "payment_method": "WhatsApp Direct"
})
assert resp.status_code == 200
data = resp.get_json()
assert data["count"] == 3
assert len(data["keys_list"]) == 3
print("[OK] POST /api/v1/admin/generate (batch 3 keys) successful")

# CSV download API
resp = client.get(f"/api/v1/admin/export_csv?scope=all&admin_key={ADMIN_API_KEY}")
assert resp.status_code == 200
assert resp.content_type.startswith("text/csv")
assert "Content-Disposition" in resp.headers
assert b"\xef\xbb\xbf" in resp.data[:3] # UTF-8 BOM
print("[OK] GET /api/v1/admin/export_csv (with Excel UTF-8 BOM) successful")

# Clean up test license
delete_license("MDP-LFT-TEST-1234-ABCD")
for k in data["keys_list"]:
    delete_license(k)
print("[OK] Cleaned up test records")

print("\nALL BACKEND & LICENSE MANAGER TESTS PASSED PERFECTLY!")
