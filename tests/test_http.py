from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from rsml.config import RSMLConfig
from rsml.http import create_app
from rsml.tokens import generate_token


@pytest.fixture
def config(tmp_path):
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


@pytest.fixture
def app(config):
    app = create_app(config)
    app.config["RSML_MAILER"].send = AsyncMock()
    return app


@pytest.fixture
def client(app):
    return app.test_client()


def test_subscribe_valid(client):
    resp = client.post("/list/subscribe", json={"email": "test@example.com"})
    assert resp.status_code == 202


def test_verify_valid(client, config, app):
    token = generate_token(config.server_secret, "verify", "test@example.com")
    resp = client.get(f"/list/verify?email=test@example.com&token={token}")
    assert app.config["RSML_STORAGE"].is_subscribed("test@example.com")
    assert resp.status_code == 201


def test_unsubscribe_valid(client, config, app):
    vtoken = generate_token(config.server_secret, "verify", "test@example.com")
    vresp = client.get(f"/list/verify?email=test@example.com&token={vtoken}")
    token = generate_token(config.server_secret, "unsub", "test@example.com")
    resp = client.get(f"/list/unsubscribe?email=test@example.com&token={token}")
    assert resp.status_code == 200
    assert not app.config["RSML_STORAGE"].is_subscribed("test@example.com")


def test_unsubscribe_wrong_token(client):
    resp = client.get("/list/unsubscribe?email=test@example.com&token=invalid")
    assert resp.status_code == 403


def test_verify_wrong_token(client):
    resp = client.get("/list/verify?email=test@example.com&token=invalid")
    assert resp.status_code == 403


def test_unsubscribe_non_matching(client, config):
    token = generate_token(config.server_secret, "unsub", "test@example.com")
    resp = client.get(f"/list/unsubscribe?email=invalid@example.com&token={token}")
    assert resp.status_code == 403


def test_verify_non_matching(client, config):
    token = generate_token(config.server_secret, "verify", "test@example.com")
    resp = client.get(f"/list/verify?email=invalid@example.com&token={token}")
    assert resp.status_code == 403
