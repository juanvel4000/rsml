"""a dumb flask server for the RSML endpoints"""

import hmac
from datetime import UTC, datetime
from email import policy
from email.parser import BytesParser

from email_validator import EmailNotValidError, validate_email
from flask import Blueprint, Flask, current_app, make_response, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from markupsafe import escape

from .config import RSMLConfig
from .mailer import Mailer
from .mbox import Mbox, MboxItem
from .storage import Storage
from .tokens import generate_token

http = Blueprint("rsml", __name__)
limiter = Limiter(get_remote_address)


def create_app(config: RSMLConfig) -> Flask:
    app = Flask(__name__)
    app.config["RSML_CONFIG"] = config
    app.config["RSML_STORAGE"] = Storage(config)
    app.config["RSML_MAILER"] = Mailer(config)
    app.config["RATELIMIT_STORAGE_URI"] = config.limiter_storage_uri
    app.register_blueprint(http)
    limiter.init_app(app)
    return app


@http.route("/list/subscribe", methods=["POST"])
@limiter.limit("5 per hour")
async def subscribe():
    """process an email and return a verification token"""
    mailer = current_app.config["RSML_MAILER"]
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return {"success": False, "error": "json object required"}, 400

    email = data.get("email", "")
    try:
        email = validate_email(email, check_deliverability=False).normalized
    except EmailNotValidError:
        return {"success": False, "error": "invalid email address"}, 400

    await mailer.send(mailer.generate_verification(email), email)
    return {"success": True}, 202


@http.route("/list/verify", methods=["GET"])
def verify_confirm():
    """subscribe the email using the verification token"""
    config = current_app.config["RSML_CONFIG"]
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

    return f"""
<!doctype html>
<html lang="en">
    <head>
        <title>{escape(config.display_name)} (email verification)</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
    </head>
    <body>
        <h1>{escape(config.display_name)} &lt;{escape(config.list_id)}&gt;</h1>
        <p>are you sure you want to subscribe to {escape(config.display_name)}? ({escape(email)})</p>
        <form action="/list/verify" method="POST">
            <input type="hidden" name="email" value="{escape(email)}" />
            <input type="hidden" name="token" value="{escape(token)}" />
            <button type="submit">yes, subscribe</button>
        </form>
    </body>
</html>

"""


@http.route("/list/verify", methods=["POST"])
def verify():
    config = current_app.config["RSML_CONFIG"]
    storage = current_app.config["RSML_STORAGE"]
    email = request.form.get("email")
    token = request.form.get("token")
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
    config = current_app.config["RSML_CONFIG"]
    storage = current_app.config["RSML_STORAGE"]
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
    return {"success": True}, 200


@http.route("/list/archive")
def archive():
    """retrieve an mbox containing an archive of mails"""
    config = current_app.config["RSML_CONFIG"]
    storage = current_app.config["RSML_STORAGE"]
    date = request.args.get("date") or "today"
    limit = request.args.get("limit") or config.archive_limit
    order = (request.args.get("order") or "desc").lower().strip()

    if order not in ["desc", "asc"]:
        return {"success": False, "error": "order must be either 'desc' or 'asc'"}, 400
    try:
        limit = int(limit)
    except ValueError:
        return {"success": False, "error": "limit must be an integer"}, 400
    if date == "today":
        now = datetime.now(UTC)
        year, month, day = now.year, now.month, now.day
    elif date == "all":
        year, month, day = "all", "all", "all"
    else:
        try:
            year, month, day = map(int, date.split("-"))
            # validate it by trying to make a datetime
            datetime(year, month, day)
        except ValueError:
            return {"success": False, "error": "invalid date"}, 400

    if limit <= 0:
        return {"success": False, "error": "limit must be greater than zero"}, 400

    if limit > config.archive_max:
        return {
            "success": False,
            "error": f"limit cannot be greater than max_limit ({config.archive_max})",
        }, 400

    msgs = list(storage.iter_messages(year, month, day))
    msgs = sorted(msgs, key=lambda p: p.stat().st_mtime, reverse=(order == "desc"))
    msgs = msgs[:limit]
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
