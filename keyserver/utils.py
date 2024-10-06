import json
import uuid
from datetime import datetime, timedelta
import os
from flask import request, send_from_directory, abort
from threading import Lock

lock = Lock()
ABS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__)))
KEYS_FILE = ABS_PATH + "/key_storage/keys.json"
LOGS_FILE = ABS_PATH + "/logs/request_logs.json"


def is_safe_path(basedir, path, follow_symlinks=True):
    """Ensure the requested path is within the allowed directory."""
    # Resolve the absolute path
    if follow_symlinks:
        requested_path = os.path.realpath(path)
    else:
        requested_path = os.path.abspath(path)

    # Ensure the requested file is within the allowed directory
    is_safe = os.path.commonpath([basedir, requested_path]) == basedir
    return is_safe


def serve_file(directory, filename, as_attachment=False):
    """Serve a file from the specified directory."""
    requested_path = os.path.join(directory, filename)

    if not is_safe_path(directory, requested_path):
        abort(403)  # Forbidden access

    with lock:
        if os.path.isfile(requested_path):
            return send_from_directory(directory, filename, as_attachment=as_attachment)
        else:
            abort(404)  # File not found


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


def log_request(action, key=None, machine_id=None, username=None, product_id=None, log_level="INFO"):
    # Get the client's IP address
    client_ip = (
        request.headers.get("X-Forwarded-For", request.remote_addr)
        .split(",")[0]
        .strip()
    )
    
    # Create a log entry
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "level": log_level,
        "client": {
            "ip_address": client_ip,
            "username": username
        },
        "action": action,
        "details": {
            "key": key,
            "product_id": product_id,
            "machine_id": machine_id
        },
    }
    
    # Ensure the log file exists and load existing logs
    if os.path.exists(LOGS_FILE):
        with open(LOGS_FILE, "r") as log_file:
            try:
                logs = json.load(log_file)  # Load existing logs
            except json.JSONDecodeError:
                logs = []  # Start with an empty list if the file is empty or corrupt
    else:
        logs = []  # Start with an empty list if the file does not exist

    # Append the new log entry to the logs list
    logs.append(log_entry)

    # Write the updated logs back to the file
    with open(LOGS_FILE, "w") as log_file:
        json.dump(logs, log_file, indent=4)  # Write the logs as formatted JSON



