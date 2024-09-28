from flask import request
import os

if admin_password := os.getenv("ADMIN_PASSWORD"):
    if not admin_password:
        raise RuntimeError("ADMIN_PASSWORD is not set")

if billing_password := os.getenv("BILLING_PASSWORD"):
    if not billing_password:
        raise RuntimeError("BILLING_PASSWORD is not set")

USERS = {
    "admin": {"password": admin_password, "role": "admin"},
    "billing": {"password": billing_password, "role": "user"},
}


def check_auth():
    auth = request.authorization
    if (
        not auth
        or auth.username not in USERS
        or auth.password != USERS[auth.username]["password"]
    ):
        return None
    return USERS[auth.username]
