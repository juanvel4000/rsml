"""system mail generator"""

import copy
from collections.abc import Iterable
from email import policy
from email.message import EmailMessage
from email.parser import BytesParser
from email.utils import formatdate
from urllib.parse import quote as quote_escape

import aiosmtplib
from email_validator import EmailNotValidError, validate_email

from .config import RSMLConfig
from .tokens import generate_token


class Mailer:
    """class for mailer"""

    def __init__(self, config: RSMLConfig):
        self.config = config

    def add_headers(self, email: EmailMessage) -> EmailMessage:
        """add identification headers, specified by config.py"""
        email["List-ID"] = f"{self.config.display_name} <{self.config.list_id}>"
        if self.config.precedence == "list":
            email["Precedence"] = "list"
        if self.config.fix_date:
            del email["Date"]
            email["Date"] = formatdate()
        return email

    def add_unsubscribe_headers(
        self, email: str, message: EmailMessage
    ) -> EmailMessage:
        """add unsubscribe headers for mass-forwarded mails"""
        try:
            email = validate_email(email, check_deliverability=False).normalized
        except EmailNotValidError:
            raise ValueError("invalid email")

        token = generate_token(self.config.server_secret, "unsub", email)
        message["List-Unsubscribe"] = (
            f"<{self.config.http_url}/list/unsubscribe?email={quote_escape(email)}&token={token}>"
        )
        message["List-Unsubscribe-Post"] = "List-Unsubscribe=One-Click"

        return message

    def generate_verification(self, email: str) -> EmailMessage:
        """generate a verification mail"""
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
            f"<{self.config.http_url}/list/verify?email={quote_escape(email)}&token={token}>"
        )
        return msg

    async def forward_message(
        self, raw: bytes, subscribers: Iterable[str]
    ) -> list[str]:
        """forward a received mail to all the subscribers, returns list of failed addresses"""
        og = self.add_headers(BytesParser(policy=policy.default).parsebytes(raw))
        failed = []
        for sub in subscribers:
            try:
                msg = copy.deepcopy(og)
                msg = self.add_unsubscribe_headers(sub, msg)
                _ = await self.send(msg, sub)
            except Exception:
                failed.append(sub)
        return failed

    async def send(self, message: EmailMessage, recipient: str):
        """thin wrapper around aiosmtplib.send"""
        return await aiosmtplib.send(
            message,
            hostname=self.config.relay_host,
            port=self.config.relay_port,
            recipients=[recipient],
        )

    def __repr__(self) -> str:
        return f"Mailer(config={self.config})"
