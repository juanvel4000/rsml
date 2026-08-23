"""RFC 4155-compliant mbox manager"""

from dataclasses import dataclass
from datetime import datetime
from email.message import EmailMessage


@dataclass
class MboxItem:
    """a representation of an mbox entry"""

    sender: str
    timestamp: datetime
    message: EmailMessage

    def to_bytes(self) -> bytes:
        result = bytearray()

        day = f"{self.timestamp.day:2d}"
        time = self.timestamp.strftime(f"%a %b {day} %H:%M:%S %Y")

        result.extend(f"From {self.sender} {time}\n".encode("ascii"))

        message = self.message.as_bytes()

        for line in message.splitlines(keepends=True):
            idx = 0
            while idx < len(line) and line[idx : idx + 1] == b">":
                idx += 1
            if line[idx:].startswith(b"From "):
                result.extend(b">")

            result.extend(line)

        if not result.endswith(b"\n"):
            result.extend(b"\n")
        result.extend(b"\n")

        return bytes(result)


class Mbox:
    """a representation of an mbox"""

    def __init__(self, messages: list[MboxItem]):
        self.messages = messages

    def to_bytes(self) -> bytes:
        return b"".join(message.to_bytes() for message in self.messages)

    def __repr__(self):
        return f"Mbox(messages={self.messages})"
