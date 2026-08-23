"""a flask server for the RSML endpoints; dumb"""

import os
import sys

from email_validator import EmailNotValidError, validate_email
from flask import Flask, request

from .config import load_config
from .tokens import generate_token

http = Flask(__name__)

# TODO: proper config loading
config = load_config(os.environ.get("RSML_CONFIG", "rsml.toml"))


@http.route("/list/subscribe", methods=["POST"])
def subscribe():
    data = request.get_json()

    if not isinstance(data, dict):
        return {"success": False, "error": "json object required"}, 400

    email = data.get("email", "")
    try:
        email = validate_email(email, check_deliverability=False).normalized
    except EmailNotValidError:
        return {"success": False, "error": "invalid email address"}, 400

    # TODO: send the token via lmtp/smtp instead of sending it through here
    token = generate_token(config.server_secret, "verify", email)
    return {"success": True, "token": token}, 201
