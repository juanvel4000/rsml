from unittest.mock import AsyncMock

import pytest

from rsml.config import RSMLConfig
from rsml.lmtp import LMTPHandler
from rsml.storage import Storage


@pytest.fixture
def config(tmp_path) -> RSMLConfig:
    return RSMLConfig(
        subscriber_db=tmp_path / "subscribers.db",
        email_directory=tmp_path / "mail",
        server_secret="placeholder",
        posting_email="list@127.0.0.1",
        display_name="rsml list",
        list_id="127.0.0.1",
        archive_limit=50,
        archive_max=100,
        posting=True,
        posting_permissions="subscribers",
        precedence="list",
        fix_date=False,
        relay_host="127.0.0.1",
        relay_port=25,
        http_url="http://127.0.0.1:8080",
        lmtp_host="127.0.0.1",
        lmtp_port=8024,
        http_host="127.0.0.1",
        http_port=8080,
    )


class FakeEnvelope:
    def __init__(self, mail_from, content=b""):
        self.mail_from = mail_from
        self.content = content
        self.rcpt_tos = []


@pytest.fixture
def handler(config):
    storage = Storage(config)
    h = LMTPHandler(config, storage)
    h.mailer.forward_message = AsyncMock()
    yield h, storage
    storage.close()


@pytest.mark.asyncio
async def test_rcpt_wrong_address(handler):
    h, _ = handler
    env = FakeEnvelope("sub@example.com")
    result = await h.handle_RCPT(None, None, env, "wrong@127.0.0.1", None)
    assert result == "550 not relaying to that address"
    assert env.rcpt_tos == []


@pytest.mark.asyncio
async def test_rcpt_posting_disabled(handler):
    h, _ = handler
    h.config.posting = False
    env = FakeEnvelope("sub@example.com")
    result = await h.handle_RCPT(None, None, env, h.config.posting_email, None)
    assert result == "550 5.7.1 delivery not authorized"
    assert env.rcpt_tos == []


@pytest.mark.asyncio
async def test_rcpt_non_subscriber_rejected(handler):
    h, _ = handler
    env = FakeEnvelope("stranger@example.com")
    result = await h.handle_RCPT(None, None, env, h.config.posting_email, None)
    assert result == "550 5.7.1 delivery not authorized"
    assert env.rcpt_tos == []


@pytest.mark.asyncio
async def test_rcpt_subscriber_accepted(handler):
    h, storage = handler
    storage.add_subscriber("sub@example.com")
    env = FakeEnvelope("sub@example.com")
    result = await h.handle_RCPT(None, None, env, h.config.posting_email, None)
    assert result == "250 OK"
    assert env.rcpt_tos == [h.config.posting_email]


@pytest.mark.asyncio
async def test_rcpt_all_perm_allows_non_subscriber(handler):
    h, _ = handler
    h.config.posting_permissions = "all"
    env = FakeEnvelope("stranger@example.com")
    result = await h.handle_RCPT(None, None, env, h.config.posting_email, None)
    assert result == "250 OK"
    assert env.rcpt_tos == [h.config.posting_email]


@pytest.mark.asyncio
async def test_rcpt_bad_sender_syntax(handler):
    h, _ = handler
    h.config.posting_permissions = "all"
    env = FakeEnvelope("sub@//example.com")
    result = await h.handle_RCPT(None, None, env, h.config.posting_email, None)
    assert result == "501 5.1.7 bad sender address syntax"
    assert env.rcpt_tos == []


@pytest.mark.asyncio
async def test_data_stores_message(handler):
    h, storage = handler
    storage.add_subscriber("sub@example.com")
    content = b"Subject: subject\r\n\r\nbody"
    env = FakeEnvelope("sub@example.com", content=content)
    result = await h.handle_DATA(None, None, env)
    assert result == "250 OK"
    stored = list(storage.iter_messages("all", "all", "all"))
    assert len(stored) == 1
    assert stored[0].read_bytes() == content


@pytest.mark.asyncio
async def test_data_forwards_to_subscriber(handler):
    h, storage = handler
    storage.add_subscriber("sub@example.com")
    content = b"Subject: subject\r\n\r\nbody"
    env = FakeEnvelope("sub@example.com", content=content)

    _ = await h.handle_DATA(None, None, env)

    h.mailer.forward_message.assert_awaited_once()
    call_args = h.mailer.forward_message.call_args
    assert call_args[0][0] == content
    assert list(call_args[0][1]) == ["sub@example.com"]
