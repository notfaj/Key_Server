import unittest
import json
import os
import sys
from datetime import datetime, timedelta

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from keyserver import app
from keyserver.utils import KEYS_FILE, ABS_PATH


class KeyManagementTest(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

        # Load credentials from .env for admin and billing users
        self.admin_auth = ("admin", os.getenv("ADMIN_PASSWORD"))
        self.billing_auth = ("billing", os.getenv("BILLING_PASSWORD"))
        self.test_product_id = "Test"

        # Create a test file in the directory if it does not exist
        self.test_file_path = os.path.join(
            ABS_PATH, ".well-known", "pki-validation", "test_file.txt"
        )
        os.makedirs(os.path.dirname(self.test_file_path), exist_ok=True)
        with open(self.test_file_path, "w") as test_file:
            test_file.write("This is a test file for validation.")

        # Create a test keys file
        self.test_key = {
            "key": "TEST-1234-5678",
            "expiration_days": 30,
            "expiration_date": (datetime.now() + timedelta(days=30)).isoformat(),
            "machine_limit": 3,
            "machine_ids": [],
            "product_id": self.test_product_id,
            "activated": False,
        }
        with open(KEYS_FILE, "w") as f:
            json.dump({"valid_keys": [self.test_key]}, f, indent=4)

    def tearDown(self):
        """Cleanup created keys for the test product."""
        self.cleanup_keys()
        try:
            os.remove(self.test_file_path)
        except PermissionError:
            pass

    def cleanup_keys(self):
        """Remove keys associated with the test product from keys.json."""
        if os.path.exists(KEYS_FILE):
            with open(KEYS_FILE, "r") as f:
                keys_data = json.load(f)
                valid_keys = keys_data.get("valid_keys", [])

            # Filter out keys related to the test product
            updated_keys = [
                key
                for key in valid_keys
                if key.get("product_id") != self.test_product_id
            ]

            # Write back the updated keys
            with open(KEYS_FILE, "w") as f:
                json.dump({"valid_keys": updated_keys}, f, indent=4)

    def test_generate_key(self):
        """Test key generation endpoint."""
        response = self.app.post(
            f"/generate-key?expiration_days=10&machine_limit=2&product_id={self.test_product_id}",
            auth=self.admin_auth,
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn("key", response.json)
        self.assertEqual(response.json["status"], "success")

    def test_activate_key(self):
        """Test key activation for a machine."""
        response = self.app.post(
            "/key?key=TEST-1234-5678&machine_id=machine-001",
            auth=self.billing_auth,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["status"], "activated")

    def test_update_expiration(self):
        """Test updating expiration for all keys of a product ID."""
        response = self.app.put(
            "/update-expiration",
            json={"product_id": self.test_product_id, "additional_days": 5},
            auth=self.admin_auth,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Updated expiration", response.json["message"])

    def test_get_request_logs(self):
        """Test retrieving request logs."""
        response = self.app.get("/request-logs", auth=self.admin_auth)
        self.assertEqual(response.status_code, 200)

    def test_get_keys_file(self):
        """Test retrieving keys file."""
        response = self.app.get("/keys", auth=self.admin_auth)
        self.assertEqual(response.status_code, 200)

    def test_delete_key(self):
        """Test deleting a key."""
        response = self.app.delete(
            "/delete-key?key=TEST-1234-5678", auth=self.admin_auth
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["status"], "success")

    def test_unauthorized_access(self):
        """Test unauthorized access to admin-only endpoints."""
        response = self.app.get("/request-logs", auth=self.billing_auth)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json["status"], "forbidden")


if __name__ == "__main__":
    unittest.main()
