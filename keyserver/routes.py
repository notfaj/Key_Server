from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request, send_file, Flask
from .utils import log_request, load_keys, save_keys, generate_key, serve_file
from .auth import USERS, check_auth
from .utils import KEYS_FILE, LOGS_FILE, ABS_PATH
import os

bp = Blueprint("main", __name__)


# Serve files from the '.well-known' directory
@bp.route("/.well-known/pki-validation/<path:filename>", methods=["GET"])
def serve_auth_file(filename):
    """Serve files from the '.well-known/pki-validation' directory."""
    directory = os.path.join(ABS_PATH, ".well-known", "pki-validation")
    return serve_file(directory, filename)


# Endpoint for hosting downloads
@bp.route("/downloads/<path:filename>", methods=["GET"])
def download_file(filename):
    """Serve downloadable files from the 'downloads' directory."""
    directory = os.path.join(ABS_PATH, "downloads")

    # Check for the 'attachment' query parameter
    as_attachment = request.args.get("attachment", "true").lower() == "true"

    return serve_file(directory, filename, as_attachment=as_attachment)


# Endpoint for generating a key
@bp.route("/generate-key", methods=["POST"])
def generate_key_route():
    user = check_auth()
    if not user:
        return (
            jsonify({"status": "unauthorized", "message": "Invalid credentials."}),
            401,
        )

    # Extract parameters from the query string using request.args
    expiration_days = request.args.get("expiration_days", default=0, type=int)
    machine_limit = request.args.get("machine_limit", default=1, type=int)
    product_id = request.args.get("product_id")

    if not product_id:  # Ensure product_id is provided
        return jsonify({"status": "error", "message": "product_id is required."}), 400

    # Generate the new key using the extracted parameters
    new_key = generate_key(expiration_days, machine_limit, product_id)
    keys = load_keys()
    keys.append(new_key)
    save_keys(keys)

    log_request(action="generate_key", key=new_key["key"], username=user["role"])

    return (
        jsonify({"status": "success", "key": new_key["key"]}),
        201,
    )


# Endpoint for activating or validating a key
@bp.route("/key", methods=["POST"])
def activate_or_validate_key():
    data = request.args  # Change to get data from args
    key = data.get("key")
    machine_id = data.get("machine_id")

    keys = load_keys()
    current_time = datetime.now().isoformat()

    for entry in keys:
        if entry["key"] == key:
            # Check if the key has expired
            if entry["expiration_date"] and current_time > entry["expiration_date"]:
                log_request(action="key_expired", key=key, machine_id=machine_id)
                return (
                    jsonify({"status": "expired", "message": "The key has expired."}),
                    400,
                )

            if machine_id in entry["machine_ids"]:
                log_request(action="validate_key", key=key, machine_id=machine_id)
                return (
                    jsonify(
                        {
                            "status": "valid",
                            "message": "The key and machine ID are valid and activated.",
                            "product_id": entry[
                                "product_id"
                            ],  # Include product_id in the response
                        }
                    ),
                    200,
                )

            if len(entry["machine_ids"]) >= entry["machine_limit"]:
                log_request(
                    action="machine_limit_exceeded", key=key, machine_id=machine_id
                )
                return (
                    jsonify(
                        {
                            "status": "limit_exceeded",
                            "message": "The key has reached its machine usage limit.",
                        }
                    ),
                    400,
                )

            # Key activation logic
            entry["machine_ids"].append(machine_id)
            entry["activated"] = True

            # Set the expiration date based on the stored expiration_days
            if entry["expiration_days"] > 0:
                entry["expiration_date"] = (
                    datetime.now() + timedelta(days=entry["expiration_days"])
                ).isoformat()

            save_keys(keys)

            log_request(action="activate_key", key=key, machine_id=machine_id)

            return (
                jsonify(
                    {
                        "status": "activated",
                        "message": "The key has been activated for the new machine.",
                        "product_id": entry[
                            "product_id"
                        ],  # Include product_id in the response
                        "expiration_date": entry[
                            "expiration_date"
                        ],  # Return the new expiration date
                    }
                ),
                200,
            )

    log_request(action="invalid_key_attempt", key=key, machine_id=machine_id)

    return jsonify({"status": "invalid", "message": "The key is invalid."}), 400


# Endpoint for to update expiration for all keys of a specific product ID
@bp.route("/update-expiration", methods=["PUT"])
def update_expiration_for_product():
    user = check_auth()
    if not user:
        return (
            jsonify({"status": "unauthorized", "message": "Invalid credentials."}),
            401,
        )
    auth = request.authorization
    username = auth.username
    user_role = USERS[username]["role"]

    if user_role != "admin":
        return (
            jsonify(
                {
                    "status": "forbidden",
                    "message": "User is not authorized to update keys.",
                }
            ),
            403,
        )

    data = request.json
    product_id = data.get("product_id")
    additional_days = data.get("additional_days")

    if not product_id or additional_days is None:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Product ID and additional_days are required.",
                }
            ),
            400,
        )

    keys = load_keys()
    updated_keys = []
    for entry in keys:
        if entry["product_id"] == product_id:
            if entry["expiration_date"]:
                current_expiration = datetime.fromisoformat(entry["expiration_date"])
                new_expiration = current_expiration + timedelta(days=additional_days)
                entry["expiration_date"] = new_expiration.isoformat()
            else:
                # If there is no expiration date, we can set it to unlimited or leave it unchanged
                entry["expiration_date"] = None
            updated_keys.append(entry)

    save_keys(keys)
    log_request(
        action="update_expiration_for_product", product_id=product_id, username=username
    )

    return (
        jsonify(
            {
                "status": "success",
                "message": f"Updated expiration for {len(updated_keys)} keys associated with product ID {product_id}.",
            }
        ),
        200,
    )


# Endpoint for retrieving request logs
@bp.route("/request-logs", methods=["GET"])
def get_request_logs():
    user = check_auth()
    if not user:
        return (
            jsonify({"status": "unauthorized", "message": "Invalid credentials."}),
            401,
        )

    auth = request.authorization
    username = auth.username
    user_role = user["role"]

    if user_role != "admin":
        return (
            jsonify(
                {
                    "status": "forbidden",
                    "message": "User is not authorized to access request logs.",
                }
            ),
            403,
        )

    if os.path.exists(LOGS_FILE):
        log_request(action="retrieve_request_logs", username=username)

        return send_file(LOGS_FILE, as_attachment=True)
    else:
        return (
            jsonify({"status": "error", "message": "Request log file not found."}),
            404,
        )


# Endpoint for retrieving keys file
@bp.route("/keys", methods=["GET"])
def get_keys_file():
    user = check_auth()
    if not user:
        return (
            jsonify({"status": "unauthorized", "message": "Invalid credentials."}),
            401,
        )

    auth = request.authorization
    username = auth.username
    user_role = user["role"]

    if user_role != "admin":
        return (
            jsonify(
                {
                    "status": "forbidden",
                    "message": "User is not authorized to access keys.",
                }
            ),
            403,
        )

    if os.path.exists(KEYS_FILE):
        log_request(action="retrieve_keys_file", username=username)
        return send_file(KEYS_FILE, as_attachment=True)
    else:
        return jsonify({"status": "error", "message": "Keys file not found."}), 404


# Endpoint to get key information
@bp.route("/key-info", methods=["GET"])
def get_key_info():
    user = check_auth()
    if not user:
        return (
            jsonify({"status": "unauthorized", "message": "Invalid credentials."}),
            401,
        )

    auth = request.authorization
    username = auth.username
    user_role = user["role"]

    if user_role != "admin":
        return (
            jsonify(
                {
                    "status": "forbidden",
                    "message": "User is not authorized to access this information.",
                }
            ),
            403,
        )

    key = request.args.get("key")
    if not key:
        return (
            jsonify({"status": "error", "message": "Key parameter is required."}),
            400,
        )

    keys = load_keys()
    for entry in keys:
        if entry["key"] == key:
            log_request(action="get_key_info", key=key, username=username)
            return jsonify({"status": "success", "key_info": entry}), 200

    return jsonify({"status": "error", "message": "Key not found."}), 404


# Endpoint to edit key information
@bp.route("/edit-key", methods=["PUT"])
def edit_key_info():
    user = check_auth()
    if not user:
        return (
            jsonify({"status": "unauthorized", "message": "Invalid credentials."}),
            401,
        )

    auth = request.authorization
    username = auth.username
    user_role = user["role"]

    if user_role != "admin":
        return (
            jsonify(
                {
                    "status": "forbidden",
                    "message": "User is not authorized to edit keys.",
                }
            ),
            403,
        )

    data = request.json
    key = data.get("key")
    if not key:
        return (
            jsonify({"status": "error", "message": "Key parameter is required."}),
            400,
        )

    keys = load_keys()
    for entry in keys:
        if entry["key"] == key:
            expiration_days = data.get("expiration_days")
            machine_limit = data.get("machine_limit")
            activated = data.get("activated")

            # Update fields
            if expiration_days is not None:
                expiration_date = (
                    (datetime.now() + timedelta(days=expiration_days)).isoformat()
                    if expiration_days > 0
                    else None
                )
                entry["expiration_date"] = expiration_date
            if machine_limit is not None:
                entry["machine_limit"] = machine_limit
            if activated is not None:
                entry["activated"] = activated

            save_keys(keys)
            log_request(action="edit_key_info", key=key, username=username)

            return (
                jsonify(
                    {
                        "status": "success",
                        "message": "Key information updated.",
                        "key_info": entry,
                    }
                ),
                200,
            )

    return jsonify({"status": "error", "message": "Key not found."}), 404


@bp.route("/delete-key", methods=["DELETE"])
def delete_key():
    # Check admin authorization
    user = check_auth()
    if not user:
        return (
            jsonify({"status": "unauthorized", "message": "Invalid credentials."}),
            401,
        )

    auth = request.authorization
    username = auth.username
    user_role = user["role"]

    if user_role != "admin":
        return (
            jsonify(
                {
                    "status": "forbidden",
                    "message": "User is not authorized to delete keys.",
                }
            ),
            403,
        )

    key = request.args.get("key")

    if not key:
        return jsonify({"status": "error", "message": "Key parameter is missing"}), 400

    keys = load_keys()

    log_request(action="delete_key", key=key, username=username)
    for entry in keys:
        if entry["key"] == key:
            keys.remove(entry)
            save_keys(keys)
            return (
                jsonify({"status": "success", "message": "Key deleted successfully"}),
                200,
            )

    return jsonify({"status": "error", "message": "Key not found"}), 404
