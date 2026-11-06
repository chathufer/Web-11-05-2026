import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "backend"))

from database import (
    init_db,
    create_license,
    update_license,
    extend_license,
    get_sales_analytics,
    export_sales_report,
    list_history,
    rollback_history,
    delete_license
)
from server import app, ADMIN_API_KEY

print("Testing Change History, Rollback System & Gift/Promotions...")

init_db()

# Clean up any leftover test keys
delete_license("MDP-LFT-GIFT-0001-TEST")
delete_license("MDP-LFT-PAID-0002-TEST")

# 1. Test Gift License Creation and Revenue Exclusion
base_analytics = get_sales_analytics()
base_rev = base_analytics["total_revenue"]
base_gifts = base_analytics["gift_licenses"]

# Create a gift license
gift_lic = create_license(
    license_key="MDP-LFT-GIFT-0001-TEST",
    plan="pro_lifetime",
    customer_name="Lucky Winner",
    customer_phone="+111222333",
    is_gift=1,
    notes="Promotion Giveaway"
)
assert gift_lic["is_gift"] == 1
assert gift_lic["price_paid"] == 0.0
assert gift_lic["payment_method"] == "Gift / Promotional Giveaway"

post_gift_analytics = get_sales_analytics()
assert post_gift_analytics["total_revenue"] == base_rev, f"Gift should not add to revenue! Got {post_gift_analytics['total_revenue']} vs {base_rev}"
assert post_gift_analytics["gift_licenses"] == base_gifts + 1
print("[OK] Gift license created and strictly excluded from sales revenue")

# 2. Create Paid License to verify paid revenue works
paid_lic = create_license(
    license_key="MDP-LFT-PAID-0002-TEST",
    plan="pro_lifetime",
    customer_name="Original Correct Buyer",
    customer_phone="+444555666",
    price_paid=24.99,
    is_gift=0,
    payment_method="WhatsApp Direct",
    notes="Original notes"
)
post_paid_analytics = get_sales_analytics()
assert abs(post_paid_analytics["total_revenue"] - (base_rev + 24.99)) < 0.01
print("[OK] Paid license correctly added to revenue ($24.99)")

# 3. Test Accidental Edit & History Logging
# Perform an accidental edit
ok = update_license(
    license_key="MDP-LFT-PAID-0002-TEST",
    customer_name="ACCIDENTAL WRONG NAME",
    customer_phone="+000000000",
    price_paid=999.99,
    notes="Accidental ruined notes"
)
assert ok

# Check history log
logs = list_history(license_key="MDP-LFT-PAID-0002-TEST", limit=10)
assert len(logs) > 0
edit_log = logs[0]
assert edit_log["action"] == "EDIT"
assert "Original Correct Buyer" in edit_log["summary"] or "ACCIDENTAL WRONG NAME" in edit_log["summary"]
assert edit_log["previous_state"] is not None
print(f"[OK] Edit captured in history log #{edit_log['id']}: {edit_log['summary']}")

# 4. Test Accidental Edit Rollback (Undo)
success, msg = rollback_history(edit_log["id"])
assert success, msg

# Verify license was completely restored to original
from database import get_license_with_activations
restored = get_license_with_activations("MDP-LFT-PAID-0002-TEST")
assert restored["customer_name"] == "Original Correct Buyer", f"Expected Original Correct Buyer, got {restored['customer_name']}"
assert restored["customer_phone"] == "+444555666"
assert abs(restored["price_paid"] - 24.99) < 0.01
assert restored["notes"] == "Original notes"
print("[OK] Accidental edit successfully rolled back to exact previous state!")

# 5. Test Flask API endpoints for history and rollback
client = app.test_client()

# GET /api/v1/admin/history
resp = client.get(f"/api/v1/admin/history?admin_key={ADMIN_API_KEY}&key=MDP-LFT-PAID-0002-TEST")
assert resp.status_code == 200
data = resp.get_json()
assert data["status"] == "success"
assert len(data["data"]) >= 2 # CREATE, EDIT, ROLLBACK
print(f"[OK] GET /api/v1/admin/history returned {len(data['data'])} audit records")

# 6. Test CSV Export with Gift column
csv_resp = client.get(f"/api/v1/admin/export_csv?scope=all&admin_key={ADMIN_API_KEY}")
assert csv_resp.status_code == 200
csv_text = csv_resp.data.decode("utf-8")
assert "Is Gift / Promotion" in csv_text
assert "YES (Free Gift)" in csv_text
print("[OK] CSV Export data sheet includes 'Is Gift / Promotion' column and flags")

# Clean up test records
delete_license("MDP-LFT-GIFT-0001-TEST")
delete_license("MDP-LFT-PAID-0002-TEST")
print("[OK] Cleaned up test records")

print("\nALL HISTORY, ROLLBACK & GIFT/PROMOTION TESTS PASSED PERFECTLY!")
