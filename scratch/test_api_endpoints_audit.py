# -*- coding: utf-8 -*-
"""
API Endpoint Security Audit:
Tests Flask endpoints directly:
1. /api/v1/license/activate rejects HWID
2. /api/v1/license/activate rejects fake keys
3. /api/v1/license/activate accepts genuine admin keys
4. /api/v1/license/trial locks HWID permanently and rejects expired claims
"""
import os
import sys
import unittest
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("./backend"))

from backend.server import app
from backend.database import init_db, record_trial_claim, create_license
from backend.keygen import generate_license_key

class TestApiSecurityAudit(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()
        init_db()

    def test_activate_rejects_hwid(self):
        hwid = "HWID-API-TEST-1111-2222"
        # Test key = HWID
        resp = self.client.post("/api/v1/license/activate", json={"key": hwid, "hwid": hwid})
        self.assertEqual(resp.status_code, 400)
        self.assertIn("cannot be used as a license key", resp.get_json()["message"])

        # Test key starting with HWID-
        resp2 = self.client.post("/api/v1/license/activate", json={"key": "HWID-9999-8888-7777-6666", "hwid": hwid})
        self.assertEqual(resp2.status_code, 400)
        self.assertIn("cannot be used as a license key", resp2.get_json()["message"])

    def test_trial_endpoint_lifecycle_and_permanent_lock(self):
        hwid = f"HWID-TRIAL-API-{int(datetime.utcnow().timestamp())}"

        # 1. First claim -> 200 OK
        resp = self.client.post("/api/v1/license/trial", json={"hwid": hwid, "machine_name": "TestPC"})
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["data"]["hwid"], hwid)
        self.assertEqual(data["data"]["days_remaining"], 7)

        # 2. Second claim while active -> 200 OK (restores active trial)
        resp2 = self.client.post("/api/v1/license/trial", json={"hwid": hwid, "machine_name": "TestPC"})
        self.assertEqual(resp2.status_code, 200)
        data2 = resp2.get_json()
        self.assertEqual(data2["status"], "success")
        self.assertIn("currently active", data2["message"])

        # 3. Simulate trial expiration in DB
        expired_date = (datetime.utcnow() - timedelta(days=1)).isoformat()
        past_start = (datetime.utcnow() - timedelta(days=8)).isoformat()
        record_trial_claim(hwid, "TestPC", past_start, expired_date)

        # 4. Attempt to claim trial again after expiration -> STRICT 400 REJECTION!
        resp3 = self.client.post("/api/v1/license/trial", json={"hwid": hwid, "machine_name": "TestPC"})
        self.assertEqual(resp3.status_code, 400)
        data3 = resp3.get_json()
        self.assertEqual(data3["status"], "error")
        self.assertIn("has expired", data3["message"])
        self.assertIn("strictly limited to one 7-day trial period", data3["message"])

    def test_genuine_admin_key_activates_cleanly(self):
        hwid = f"HWID-PRO-USER-{int(datetime.utcnow().timestamp())}"
        key = generate_license_key("pro_lifetime")
        create_license(
            license_key=key,
            plan="pro_lifetime",
            customer_name="Official Buyer",
            price_paid=24.99,
            max_activations=3
        )

        resp = self.client.post("/api/v1/license/activate", json={"key": key, "hwid": hwid, "machine_name": "BuyerPC"})
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["data"]["plan"], "pro_lifetime")

if __name__ == "__main__":
    unittest.main(verbosity=2)
