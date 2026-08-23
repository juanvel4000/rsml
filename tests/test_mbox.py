from datetime import UTC, datetime
from email.message import EmailMessage

import pytest

from rsml.mbox import Mbox, MboxItem


@pytest.fixture
def mboxitem() -> MboxItem:
    message = EmailMessage()
    message["From"] = "example@127.0.0.1"
    message["To"] = "list@127.0.0.1"
    message["Subject"] = "test"
    message.set_content("hello\r\n>From ....\r\n\r\n")

    return MboxItem("example@127.0.0.1", datetime.now(UTC), message)


@pytest.fixture
def mbox(mboxitem) -> Mbox:
    return Mbox([mboxitem])


def test_mboxitem_to_bytes(mboxitem):
    b = mboxitem.to_bytes()
    assert isinstance(b, bytes)
    assert b.startswith(b"From example@127.0.0.1 ")


def test_mbox_to_bytes(mbox):
    assert isinstance(mbox.to_bytes(), bytes)


def test_mboxrd_encoding(mboxitem):
    b = mboxitem.to_bytes()

    assert b">>From ...." in b
