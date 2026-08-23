"""a dumb flask server for the RSML endpoints"""

import hmac
import os
from datetime import UTC, datetime
from email import policy
from email.parser import BytesParser

from email_validator import EmailNotValidError, validate_email
from flask import Flask, make_response, request

from .config import load_config
from .mbox import Mbox, MboxItem
from .storage import Storage
from .tokens import generate_token

http = Flask(__name__)

# TODO: proper config loading
config = load_config(os.environ.get("RSML_CONFIG", "rsml.toml"))
storage = Storage(config)


@http.route("/list/subscribe", methods=["POST"])
def subscribe():
    """process an email and return a verification token"""
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return {"success": False, "error": "json object required"}, 400

    email = data.get("email", "")
    try:
        email = validate_email(email, check_deliverability=False).normalized
    except EmailNotValidError:
        return {"success": False, "error": "invalid email address"}, 400

    # TODO: send the token via lmtp/smtp instead of sending it through here
    token = generate_token(config.server_secret, "verify", email)
    return {"success": True, "token": token}, 202


@http.route("/list/verify")
def verify():
    """subscribe the email using the verification token"""
    token = request.args.get("token")

    email = request.args.get("email")
    if not email:
        return {"success": False, "error": "email is required"}, 400

    try:
        email = validate_email(email, check_deliverability=False).normalized
    except EmailNotValidError:
        return {"success": False, "error": "invalid email address"}, 400

    if not hmac.compare_digest(
        generate_token(config.server_secret, "verify", email), token or ""
    ):
        return {"success": False, "error": "token does not match with the email"}, 403

    storage.add_subscriber(email)
    return {"success": True}, 201


@http.route("/list/unsubscribe")
def unsubscribe():
    """unsubscribe the user using an unsubscription token"""
    token = request.args.get("token")

    email = request.args.get("email")
    if not email:
        return {"success": False, "error": "email is required"}, 400

    try:
        email = validate_email(email, check_deliverability=False).normalized
    except EmailNotValidError:
        return {"success": False, "error": "invalid email address"}, 400

    if not hmac.compare_digest(
        generate_token(config.server_secret, "unsub", email), token or ""
    ):
        return {"success": False, "error": "token does not match with the email"}, 403

    _ = storage.remove_subscriber(email)
    return {"success": True}, 201


@http.route("/list/archive")
def archive():
    """retrieve an mbox containing an archive of mails"""
    date = request.args.get("date") or "today"
    limit = request.args.get("limit") or config.archive_limit
    order = request.args.get("order") or "desc"
    try:
        limit = int(limit)
    except ValueError:
        return {"success": False, "error": "limit must be an integer"}, 400
    if date == "today":
        now = datetime.now(UTC)
        msgs = list(storage.iter_messages(now.year, now.month, now.day))
    elif date == "all":
        msgs = list(storage.iter_messages("all", "all", "all"))
    else:
        try:
            year, month, day = map(int, date.split("-"))
            msgs = list(storage.iter_messages(year, month, day))
        except ValueError:
            return {"success": False, "error": "invalid date"}, 400

    if limit > config.archive_max:
        return {
            "success": False,
            "error": f"limit cannot be greater than max_limit ({config.archive_max})",
        }, 400
    msgs = msgs[:limit]  # TODO: apply order
    final = []
    for msg in msgs:
        message = BytesParser(policy=policy.default).parsebytes(msg.read_bytes())
        date_header = message.get("Date")
        timestamp = (
            date_header.datetime
            if date_header
            else datetime.fromtimestamp(msg.stat().st_mtime, tz=UTC)
        )
        item = MboxItem(
            message["From"],
            timestamp,
            message,
        )
        final.append(item)

    response = make_response(Mbox(final).to_bytes())
    response.headers["Content-Type"] = "application/mbox"
    return response
