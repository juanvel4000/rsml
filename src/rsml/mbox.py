from dataclasses import dataclass
from datetime import datetime
from email.message import EmailMessage

from rsml.storage import Storage


@dataclass
class MboxItem:
    """a representation of an mbox entry"""

    sender: str
    timestamp: datetime
    message: EmailMessage

    def to_bytes(self) -> bytes:
        result = bytearray()

        result.extend(f"From {self.sender} {self.timestamp}\r\n".encode())

        message = self.message.as_bytes()

        for line in message.splitlines(keepends=True):
            if line.lstrip(b">").startswith(b"From "):
                result.extend(b">")

            result.extend(line)

        return bytes(result)


class Mbox:
    """a representation of an mbox"""

    def __init__(self, messages: list[MboxItem]):
        self.messages = messages

    def to_bytes(self) -> bytes:
        return b"".join(message.to_bytes() for message in self.messages)

    def __repr__(self):
        return f"Mbox(messages={self.messages})"
