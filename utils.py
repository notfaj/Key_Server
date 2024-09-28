import json
import uuid
from datetime import datetime, timedelta
import os
from flask import request

KEYS_FILE = "keys.json"


def load_keys():
    if not os.path.exists(KEYS_FILE):
        with open(KEYS_FILE, "w") as f:
            json.dump({"valid_keys": []}, f, indent=4)
    with open(KEYS_FILE, "r") as f:
        keys = json.load(f)["valid_keys"]
        return remove_expired_keys(keys)


def save_keys(keys):
    with open(KEYS_FILE, "w") as f:
        json.dump({"valid_keys": keys}, f, indent=4)


def remove_expired_keys(keys):
    current_time = datetime.now().isoformat()
    updated_keys = []
    for key in keys:
        if key["expiration_date"] and current_time > key["expiration_date"]:
            continue  # Skip expired keys
        updated_keys.append(key)
    if len(updated_keys) != len(keys):
        save_keys(updated_keys)
    return updated_keys


def generate_key(expiration_days, machine_limit, product_id):
    key = str(uuid.uuid4())
    expiration_date = (
        None
        if expiration_days == 0
        else (datetime.now() + timedelta(days=expiration_days)).isoformat()
    )
    return {
        "key": key,
        "product_id": product_id,
        "machine_ids": [],
        "activated": False,
        "expiration_date": expiration_date,
        "machine_limit": machine_limit,
    }


def log_request(action, key=None, machine_id=None, username=None, product_id=None):
    client_ip = (
        request.headers.get("X-Forwarded-For", request.remote_addr)
        .split(",")[0]
        .strip()
    )
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "ip_address": client_ip,
        "action": action,
        "key": key,
        "machine_id": machine_id,
        "username": username,
        "product_id": product_id,
    }
    with open("request_logs.json", "a") as log_file:
        log_file.write(json.dumps(log_entry) + "\n")
