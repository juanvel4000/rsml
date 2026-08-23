"""send/receive emails from an MTA using lmtp"""

from aiosmtpd.controller import Controller
from aiosmtpd.lmtp import LMTP

from .config import RSMLConfig
from .mailer import Mailer
from .storage import Storage


class LMTPController(Controller):
    def factory(self):
        return LMTP(self.handler, **self.SMTP_kwargs)


class LMTPHandler:
    def __init__(self, config: RSMLConfig, storage: Storage):
        self.config = config
        self.storage = storage
        self.mailer = Mailer(config)

    async def handle_RCPT(
        self, server, session, envelope, address, rcpt_options
    ) -> str:
        if address.lower() != self.config.posting_email.lower():
            return "550 not relaying to that address"

        if not self.config.posting:
            return "550 5.7.1 delivery not authorized"

        if (
            self.config.posting_permissions == "subscribers"
            and not self.storage.is_subscribed(envelope.mail_from)
        ):
            return "550 5.7.1 delivery not authorized"
        envelope.rcpt_tos.append(address)
        return "250 OK"

    async def handle_DATA(self, server, session, envelope) -> str:

        self.storage.store_message(envelope.content)
        await self.mailer.forward_message(
            envelope.content, self.storage.get_subscribers()
        )
        return "250 OK"


def controller_init(config: RSMLConfig) -> LMTPController:
    storage = Storage(config)
    controller = LMTPController(
        LMTPHandler(config, storage), hostname=config.lmtp_host, port=config.lmtp_port
    )

    controller.start()

    return controller
