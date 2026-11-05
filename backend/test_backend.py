"""
Automated Test Suite for Media Downloader Pro Backend & Licensing
Tests keygen, database operations, Flask API endpoints, and HWID binding.
"""

import os
import sys
import json
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import init_db, create_license, list_all_licenses
from keygen import (
    generate_license_key,
    get_hardware_id,
    calculate_expiry,
    sign_license_payload,
    verify_license_payload
)
from server import app, ADMIN_API_KEY


class TestBackend(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.hwid_1 = "HWID-TEST-AAAA-1111-2222"
        self.hwid_2 = "HWID-TEST-BBBB-3333-4444"

    def test_01_keygen_and_signature(self):
        """Test key format and HMAC signature."""
        key = generate_license_key("pro_yearly")
        self.assertTrue(key.startswith("MDP-YEA-"))
        self.assertEqual(len(key.split("-")), 5)

        payload = {"license_key": key, "plan": "pro_yearly", "hwid": self.hwid_1}
        payload["signature"] = sign_license_payload(payload)

        self.assertTrue(verify_license_payload(payload))

        # Tampering test
        tampered = dict(payload)
        tampered["plan"] = "pro_lifetime"
        self.assertFalse(verify_license_payload(tampered))

    def test_02_admin_generate_api(self):
        """Test Admin Key Generation API."""
        resp = self.client.post("/api/v1/admin/generate", json={
            "admin_key": ADMIN_API_KEY,
            "plan": "pro_yearly",
            "customer_name": "Alice Wonderland",
            "customer_email": "alice@example.com",
            "max_activations": 1
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "success")
        key = data["data"]["license_key"]
        self.assertTrue(key.startswith("MDP-YEA-"))

    def test_03_activation_and_device_limit(self):
        """Test device binding and 1-PC enforcement."""
        # Generate 1-device key
        resp = self.client.post("/api/v1/admin/generate", json={
            "admin_key": ADMIN_API_KEY,
            "plan": "pro_monthly",
            "customer_name": "Bob Builder",
            "max_activations": 1
        })
        key = resp.get_json()["data"]["license_key"]

        # Activate on Device 1 -> SUCCESS
        act1 = self.client.post("/api/v1/license/activate", json={
            "key": key,
            "hwid": self.hwid_1,
            "machine_name": "PC-BOB-DESKTOP"
        })
        self.assertEqual(act1.status_code, 200)
        self.assertEqual(act1.get_json()["status"], "success")
        self.assertTrue("signature" in act1.get_json()["data"])

        # Activate on Device 2 -> SHOULD FAIL (limit 1)
        act2 = self.client.post("/api/v1/license/activate", json={
            "key": key,
            "hwid": self.hwid_2,
            "machine_name": "PC-BOB-LAPTOP"
        })
        self.assertEqual(act2.status_code, 400)
        self.assertIn("limit reached", act2.get_json()["message"].lower())

        # Heartbeat on Device 1 -> SUCCESS
        ver1 = self.client.post("/api/v1/license/verify", json={
            "key": key,
            "hwid": self.hwid_1
        })
        self.assertEqual(ver1.status_code, 200)

        # Deactivate Device 1
        deact = self.client.post("/api/v1/license/deactivate", json={
            "key": key,
            "hwid": self.hwid_1
        })
        self.assertEqual(deact.status_code, 200)

        # Now Device 2 can activate -> SUCCESS
        act2_retry = self.client.post("/api/v1/license/activate", json={
            "key": key,
            "hwid": self.hwid_2,
            "machine_name": "PC-BOB-LAPTOP"
        })
        self.assertEqual(act2_retry.status_code, 200)
        self.assertEqual(act2_retry.get_json()["status"], "success")

    def test_04_revocation(self):
        """Test license revocation."""
        resp = self.client.post("/api/v1/admin/generate", json={
            "admin_key": ADMIN_API_KEY,
            "plan": "pro_lifetime",
            "customer_name": "Charlie"
        })
        key = resp.get_json()["data"]["license_key"]

        # Revoke
        rev = self.client.post("/api/v1/admin/revoke", json={
            "admin_key": ADMIN_API_KEY,
            "key": key
        })
        self.assertEqual(rev.status_code, 200)

        # Activation attempt on revoked key should fail
        act = self.client.post("/api/v1/license/activate", json={
            "key": key,
            "hwid": self.hwid_1
        })
        self.assertEqual(act.status_code, 400)
        self.assertIn("revoked", act.get_json()["message"].lower())


if __name__ == "__main__":
    unittest.main()
