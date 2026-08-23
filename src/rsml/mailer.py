from email.message import EmailMessage
from email.utils import formatdate

from email_validator import EmailNotValidError, validate_email

from .config import RSMLConfig
from .tokens import generate_token


class Mailer:
    def __init__(self, config: RSMLConfig):
        self.config = config

    def add_headers(self, email: EmailMessage) -> EmailMessage:
        email["List-ID"] = f"{self.config.display_name} <{self.config.list_id}>"
        if self.config.precedence == "list":
            email["Precedence"] = "list"
        if self.config.fix_date:
            email["Date"] = formatdate()
        return email

    def add_unsubscribe_headers(
        self, email: str, message: EmailMessage
    ) -> EmailMessage:
        try:
            email = validate_email(email, check_deliverability=False).normalized
        except EmailNotValidError:
            raise ValueError("invalid email")

        token = generate_token(self.config.server_secret, "unsub", email)
        # TODO: support an actual http url in config.py
        # use the list_id for now
        message["List-Unsubscribe"] = (
            f"<https://{self.config.list_id}/list/unsubscribe?email={email}&token={token}>"
        )
        message["List-Unsubscribe-Post"] = "List-Unsubscribe=One-Click"

        return message

    def generate_verification(self, email: str) -> bytes:
        try:
            email = validate_email(email, check_deliverability=False).normalized
        except EmailNotValidError:
            raise ValueError("invalid email")

        token = generate_token(self.config.server_secret, "verify", email)

        msg = EmailMessage()
        msg["From"] = self.config.posting_email
        msg["To"] = email
        msg["Subject"] = f"{self.config.display_name} - email verification"
        msg = self.add_headers(msg)

        msg.set_content(
            f"<https://{self.config.list_id}/list/verify?email={email}&token={token}>"
        )
        return msg.as_bytes()

    def __repr__(self) -> str:
        return f"Mailer(config={self.config})"
