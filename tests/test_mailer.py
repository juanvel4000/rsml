from email.message import EmailMessage

import pytest

from rsml.config import RSMLConfig
from rsml.mailer import Mailer
from rsml.tokens import generate_token


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
        fix_date=True,
        relay_host="127.0.0.1",
        relay_port=25,
        http_url="http://127.0.0.1:8080",
        lmtp_host="127.0.0.1",
        lmtp_port=8024,
        http_host="127.0.0.1",
        http_port=8080,
    )


def test_add_headers(config):
    mailer = Mailer(config)
    message = EmailMessage()
    message["From"] = "test@example.com"
    message["To"] = config.posting_email
    message["Date"] = None
    fixed = mailer.add_headers(message)

    assert fixed["List-ID"] == f"{config.display_name} <{config.list_id}>"
    assert fixed["Precedence"] == "list"
    assert message["Date"] != None


def test_add_unsubscribe_headers(config):
    mailer = Mailer(config)
    message = EmailMessage()
    message["From"] = "test@example.com"
    message["To"] = config.posting_email
    message["Date"] = None
    fixed = mailer.add_unsubscribe_headers("receiver@example.com", message)

    expected_token = generate_token(
        config.server_secret, "unsub", "receiver@example.com"
    )
    expected_url = f"<{config.http_url}/list/unsubscribe?email=receiver@example.com&token={expected_token}>"
    assert fixed["List-Unsubscribe"] == expected_url
    assert fixed["List-Unsubscribe-Post"] == "List-Unsubscribe=One-Click"


def test_generate_verification(config):
    mailer = Mailer(config)
    message = mailer.generate_verification("receiver@example.com")

    expected_token = generate_token(
        config.server_secret, "verify", "receiver@example.com"
    )
    expected_url = f"<{config.http_url}/list/verify?email=receiver@example.com&token={expected_token}>"
    assert message["Subject"] == f"{config.display_name} - email verification"
    assert expected_url in message.get_content()
