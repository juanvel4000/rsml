from pathlib import Path

from rsml.config import RSMLConfig, load_config, validate_config


def test_load_config_file():
    config = load_config(Path(__file__).parent.parent / "rsml.toml.example")

    assert config.server_secret
    assert config.posting_email == "list@127.0.0.1"
    assert config.display_name == "rsml list"


def test_validate_config():
    config = RSMLConfig(
        subscriber_db=Path("/var/lib/rsml/subscribers.db"),
        email_directory=Path("/var/lib/rsml/mail"),
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

    assert validate_config(config) is None
