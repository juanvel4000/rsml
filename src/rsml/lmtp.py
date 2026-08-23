"""send/receive emails from an MTA using lmtp"""

from aiosmtpd.controller import Controller
from aiosmtpd.lmtp import LMTP

from .config import RSMLConfig
from .storage import Storage


class LMTPController(Controller):
    def factory(self):
        return LMTP(self.handler, **self.SMTP_kwargs)


class LMTPHandler:
    def __init__(self, config: RSMLConfig, storage: Storage):
        self.config = config
        self.storage = storage

    async def handle_RCPT(
        self, server, session, envelope, address, rcpt_options
    ) -> str:
        if address != self.config.posting_email:
            return "550 not relaying to that address"
        envelope.rcpt_tos.append(address)
        return "250 OK"

    async def handle_DATA(self, server, session, envelope) -> str:
        self.storage.store_message(envelope.content)
        return "250 OK"


def controller_init(config: RSMLConfig) -> LMTPController:
    storage = Storage(config)
    # TODO: receive hostname and port from config
    controller = LMTPController(
        LMTPHandler(config, storage), hostname="127.0.0.1", port=8024
    )

    controller.start()

    return controller
