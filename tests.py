import unittest
import json
import os
import base64
from app import app


class KeyManagementTest(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

        # Load credentials from .env for admin and billing users
        self.admin_auth = ("admin", os.getenv("ADMIN_PASSWORD"))
        self.billing_auth = ("billing", os.getenv("BILLING_PASSWORD"))
        self.test_product_id = "test_product"

    def tearDown(self):
        """Cleanup created keys for the test product."""
        self.cleanup_keys()

    def cleanup_keys(self):
        """Remove keys associated with the test product from keys.json."""
        if os.path.exists("keys.json"):
            with open("keys.json", "r") as f:
                keys_data = json.load(f)
                valid_keys = keys_data["valid_keys"]

            # Filter out keys related to the test product
            updated_keys = [
                key
                for key in valid_keys
                if key.get("product_id") != self.test_product_id
            ]

            # Write back the updated keys
            with open("keys.json", "w") as f:
                json.dump({"valid_keys": updated_keys}, f, indent=4)

    def test_create_key(self):
        response = self.app.post(
            "/generate-key",
            headers={
                "Authorization": "Basic "
                + base64.b64encode(
                    f"{self.admin_auth[0]}:{self.admin_auth[1]}".encode()
                ).decode()
            },
            json={
                "expiration_days": 10,
                "machine_limit": 5,
                "product_id": self.test_product_id,
            },
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode())
        self.assertIn("key", data)

    def test_activate_key(self):
        # Create a key first
        create_response = self.app.post(
            "/generate-key",
            headers={
                "Authorization": "Basic "
                + base64.b64encode(
                    f"{self.admin_auth[0]}:{self.admin_auth[1]}".encode()
                ).decode()
            },
            json={
                "expiration_days": 10,
                "machine_limit": 1,
                "product_id": self.test_product_id,
            },
        )
        created_key = json.loads(create_response.data.decode())["key"]

        # Activate the created key
        activate_response = self.app.post(
            "/key", json={"key": created_key, "machine_id": "machine_123"}
        )
        self.assertEqual(activate_response.status_code, 200)
        data = json.loads(activate_response.data.decode())
        self.assertEqual(data["status"], "activated")

    def test_invalid_key(self):
        response = self.app.post(
            "/key", json={"key": "invalid_key", "machine_id": "machine_123"}
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data.decode())
        self.assertEqual(data["status"], "invalid")

    def test_key_info(self):
        # Create a key first
        create_response = self.app.post(
            "/generate-key",
            headers={
                "Authorization": "Basic "
                + base64.b64encode(
                    f"{self.admin_auth[0]}:{self.admin_auth[1]}".encode()
                ).decode()
            },
            json={
                "expiration_days": 10,
                "machine_limit": 5,
                "product_id": self.test_product_id,
            },
        )
        created_key = json.loads(create_response.data.decode())["key"]

        # Get key info
        response = self.app.get(
            f"/key-info?key={created_key}",
            headers={
                "Authorization": "Basic "
                + base64.b64encode(
                    f"{self.admin_auth[0]}:{self.admin_auth[1]}".encode()
                ).decode()
            },
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode())
        self.assertEqual(data["status"], "success")

    def test_expiration_for_product(self):
        response = self.app.put(
            "/update-expiration",
            headers={
                "Authorization": "Basic "
                + base64.b64encode(
                    f"{self.admin_auth[0]}:{self.admin_auth[1]}".encode()
                ).decode()
            },
            json={"product_id": self.test_product_id, "additional_days": 5},
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode())
        self.assertEqual(data["status"], "success")

    def test_edit_key_info(self):
        # Create a key first
        create_response = self.app.post(
            "/generate-key",
            headers={
                "Authorization": "Basic "
                + base64.b64encode(
                    f"{self.admin_auth[0]}:{self.admin_auth[1]}".encode()
                ).decode()
            },
            json={
                "expiration_days": 10,
                "machine_limit": 5,
                "product_id": self.test_product_id,
            },
        )
        created_key = json.loads(create_response.data.decode())["key"]

        # Edit the key
        response = self.app.put(
            "/edit-key",
            headers={
                "Authorization": "Basic "
                + base64.b64encode(
                    f"{self.admin_auth[0]}:{self.admin_auth[1]}".encode()
                ).decode()
            },
            json={"key": created_key, "expiration_days": 20, "machine_limit": 10},
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode())
        self.assertEqual(data["status"], "success")

    def test_request_logs_access(self):
        # Test access to request logs as admin
        response = self.app.get(
            "/request-logs",
            headers={
                "Authorization": "Basic "
                + base64.b64encode(
                    f"{self.admin_auth[0]}:{self.admin_auth[1]}".encode()
                ).decode()
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("application/json", response.content_type)

        # Test access to request logs as non-admin
        response = self.app.get(
            "/request-logs",
            headers={
                "Authorization": "Basic "
                + base64.b64encode(
                    f"{self.billing_auth[0]}:{self.billing_auth[1]}".encode()
                ).decode()
            },
        )
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.data.decode())
        self.assertEqual(data["status"], "forbidden")

    def test_keys_file_access(self):
        # Test access to keys file as admin
        response = self.app.get(
            "/keys",
            headers={
                "Authorization": "Basic "
                + base64.b64encode(
                    f"{self.admin_auth[0]}:{self.admin_auth[1]}".encode()
                ).decode()
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("application/json", response.content_type)

        # Test access to keys file as non-admin
        response = self.app.get(
            "/keys",
            headers={
                "Authorization": "Basic "
                + base64.b64encode(
                    f"{self.billing_auth[0]}:{self.billing_auth[1]}".encode()
                ).decode()
            },
        )
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.data.decode())
        self.assertEqual(data["status"], "forbidden")


if __name__ == "__main__":
    unittest.main()
