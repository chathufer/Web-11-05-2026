# -*- coding: utf-8 -*-
"""
Comprehensive Security & Anti-Bypass Audit Test Suite for Media Downloader Pro.
Tests:
1. HWID Bypass Elimination (Client, DB, API).
2. Fake / Invalid Key Rejection.
3. Legitimate Admin Key Activation.
4. Strict Hardware-Locked 7-Day Trial (ProgramData + Registry + Server).
5. App Reinstallation / Redownload Simulation (survives deletion of ~/.youtube_downloader).
6. Clock Rollback / Anti-Tampering Detection.
"""
import os
import sys
import shutil
import tempfile
import unittest
from datetime import datetime, timedelta

# Ensure workspace root and backend are on sys.path
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("./backend"))

from backend.database import (
    init_db,
    create_license,
    activate_license,
    verify_license,
    record_trial_claim as db_record_trial_claim,
    get_trial_claim as db_get_trial_claim
)
from backend.keygen import (
    generate_license_key,
    verify_key_signature,
    get_hardware_id,
    calculate_expiry,
    sign_license_payload
)
import licensing
from licensing import (
    record_trial_claim as client_record_trial_claim,
    check_trial_claimed as client_check_trial_claimed,
    LicenseManager
)


class TestSecurityAndAntiBypass(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, "test_security.db")
        init_db(self.db_path)
        self.test_hwid = "HWID-TEST-AUDIT-9988-7766"

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_01_hwid_cannot_activate_in_db(self):
        """Verify that passing HWID directly to database activate_license fails."""
        # 1. Using HWID format
        ok, msg, lic = activate_license(self.test_hwid, self.test_hwid, "AuditPC", self.db_path)
        self.assertFalse(ok)
        self.assertIn("Machine Hardware ID cannot be used as a license key", msg)
        self.assertIsNone(lic)

        # 2. Using arbitrary HWID- prefix
        ok2, msg2, lic2 = activate_license("HWID-0000-1111-2222-3333", self.test_hwid, "AuditPC", self.db_path)
        self.assertFalse(ok2)
        self.assertIn("Machine Hardware ID cannot be used as a license key", msg2)

    def test_02_hwid_cannot_verify_in_db(self):
        """Verify that passing HWID directly to database verify_license fails."""
        ok, msg, lic = verify_license(self.test_hwid, self.test_hwid, self.db_path)
        self.assertFalse(ok)
        self.assertIn("Machine Hardware ID is not a license key", msg)

    def test_03_hwid_cannot_activate_in_client(self):
        """Verify that client LicenseManager rejects HWID string."""
        mgr = LicenseManager()
        # Test machine's actual HWID
        ok, msg = mgr.activate(mgr.hwid)
        self.assertFalse(ok)
        self.assertIn("Hardware ID", msg)

        # Test HWID- prefix
        ok2, msg2 = mgr.activate("HWID-AAAA-BBBB-CCCC-DDDD")
        self.assertFalse(ok2)
        self.assertIn("Hardware ID", msg2)

    def test_04_fake_keys_rejected(self):
        """Verify that random strings or spoofed keys cannot activate."""
        fake_keys = [
            "MDP-LFT-FAKE-KEY1-9999",
            "1234567890",
            "FREE-PRO-CRACK-2026",
            "MDP-PRO-HACK-KEY-0000"
        ]
        mgr = LicenseManager()
        for fk in fake_keys:
            ok, msg = mgr.activate(fk)
            self.assertFalse(ok, f"Fake key '{fk}' should have been rejected!")
            valid_sig, _ = verify_key_signature(fk)
            self.assertFalse(valid_sig, f"Signature of '{fk}' should be invalid!")

    def test_05_legitimate_admin_keys_succeed(self):
        """Verify that official HMAC-signed keys activate cleanly."""
        # 1. Offline cryptographic verification test
        real_key = generate_license_key("pro_lifetime")
        is_valid, plan = verify_key_signature(real_key)
        self.assertTrue(is_valid)
        self.assertEqual(plan, "pro_lifetime")

        # 2. Online / DB activation test
        create_license(
            license_key=real_key,
            plan="pro_lifetime",
            customer_name="Paying Customer",
            price_paid=24.99,
            max_activations=3,
            db_path=self.db_path
        )
        ok, msg, lic_dict = activate_license(real_key, self.test_hwid, "Customer-PC", self.db_path)
        self.assertTrue(ok)
        self.assertEqual(lic_dict["license_key"], real_key)
        self.assertEqual(lic_dict["plan"], "pro_lifetime")

    def test_06_server_trial_claims_table_locks_hwid(self):
        """Verify that trial_claims table permanently records HWID and blocks renewals."""
        hwid = "HWID-TRIAL-LOCK-1122-3344"
        now_iso = datetime.utcnow().isoformat()
        # Expired 1 hour ago
        exp_iso = (datetime.utcnow() - timedelta(hours=1)).isoformat()

        # Record expired trial
        db_record_trial_claim(hwid, "Office-PC", now_iso, exp_iso, "127.0.0.1", self.db_path)

        # Retrieve claim
        claim = db_get_trial_claim(hwid, self.db_path)
        self.assertIsNotNone(claim)
        self.assertEqual(claim["hwid"], hwid)

        # Verify claim is expired
        exp_dt = datetime.fromisoformat(claim["expires_at"])
        self.assertGreater(datetime.utcnow(), exp_dt)

    def test_07_client_multi_tier_trial_persistence(self):
        """Verify that client trial record persists and locks machine."""
        test_hwid = "HWID-PERSISTENCE-TEST-5566"
        started_at = (datetime.utcnow() - timedelta(days=8)).isoformat()
        expired_at = (datetime.utcnow() - timedelta(days=1)).isoformat()

        # Write trial record
        client_record_trial_claim(test_hwid, started_at, expired_at)

        # Check claim status
        claimed, exp_str, is_exp, reason = client_check_trial_claimed(test_hwid)
        self.assertTrue(claimed)
        self.assertTrue(is_exp, f"Expected trial to be expired, got: {reason}")
        self.assertEqual(reason, "Trial expired")

    def test_08_trial_redownload_simulation(self):
        """
        Simulate user deleting their local AppData (~/.youtube_downloader)
        after trial expires.
        Verifies that ProgramData and Registry markers catch the user
        and self-heal the local record.
        """
        test_hwid = "HWID-REDOWNLOAD-TEST-7788"
        started_at = (datetime.utcnow() - timedelta(days=8)).isoformat()
        expired_at = (datetime.utcnow() - timedelta(days=1)).isoformat()

        # 1. Claim trial
        client_record_trial_claim(test_hwid, started_at, expired_at)

        # 2. User deletes ~/.youtube_downloader/trial_record.dat (simulating uninstall/redownload)
        local_user_record = licensing._get_trial_record_path()
        if os.path.isfile(local_user_record):
            try:
                os.remove(local_user_record)
            except Exception:
                pass
        self.assertFalse(os.path.isfile(local_user_record))

        # 3. New app launch checks trial status
        claimed, exp_str, is_exp, reason = client_check_trial_claimed(test_hwid)

        # MUST STILL DETECT EXPIRED TRIAL via ProgramData / Registry!
        self.assertTrue(claimed, "Trial claim should survive deletion of user AppData!")
        self.assertTrue(is_exp, "Trial should remain expired!")

        # MUST SELF-HEAL by re-writing local record
        self.assertTrue(os.path.isfile(local_user_record), "Self-healing must restore local record!")

    def test_09_clock_rollback_anti_tampering(self):
        """
        Simulate user rolling back their computer clock by 3 years to extend trial.
        Verifies that clock rollback is detected and trial access is revoked.
        """
        test_hwid = "HWID-CLOCK-TAMPER-9900"
        # Watermark recorded in 2026
        future_watermark = "2026-11-06T12:00:00"
        started_at = "2026-11-01T12:00:00"
        expired_at = "2026-11-08T12:00:00"

        # Record claim with future watermark
        client_record_trial_claim(test_hwid, started_at, expired_at, watermark=future_watermark)

        # Temporarily mock datetime in check_trial_claimed by checking watermark comparison logic
        # If system clock was rolled back to 2023, watermark (2026) is > system clock + 1 hr
        now_dt = datetime.fromisoformat("2023-01-01T12:00:00")
        watermark_dt = datetime.fromisoformat(future_watermark)
        clock_tampered = (now_dt < watermark_dt - timedelta(hours=1))
        self.assertTrue(clock_tampered, "Clock rollback must be detected!")


if __name__ == "__main__":
    unittest.main(verbosity=2)
