import hashlib
import hmac
from flask import request
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv("credentials.env")

# Access the environment variables using os.getenv()
admin_password = os.getenv("ADMIN_PASSWORD")
billing_password = os.getenv("BILLING_PASSWORD")
sellsn_secret_key = os.getenv("SELLSN_SECRET_KEY")

USERS = {
    "admin": {"password": admin_password, "role": "admin"},
    "billing": {"password": billing_password, "role": "user"},
}


def check_auth():
    # Check for the authorization header
    auth = request.authorization

    # Check if the request is from the SellSN API
    if "X-Webhook-Signature" in request.headers:
        # Step 1: Get the received signature from the request headers
        recv_signature = bytes.fromhex(request.headers["X-Webhook-Signature"])

        # Step 2: Get the request body (the raw payload)
        request_body = request.data

        # Step 3: Generate a HMAC signature using the body and the secret key
        signature = hmac.new(
            sellsn_secret_key, request_body, hashlib.sha256
        ).hexdigest()

        # Step 4: Compare the received signature with the generated one
        if not hmac.compare_digest(recv_signature, bytes.fromhex(signature)):
            print("Webhook request could not be verified as legitimate")
            return None

        print("Webhook verified successfully")
        return {
            "role": "billing_confirmation"
        }  # Indicate this is a billing confirmation call

    # Standard authentication check for user credentials
    if (
        not auth
        or auth.username not in USERS
        or auth.password != USERS[auth.username]["password"]
    ):
        return None

    return USERS[auth.username]
