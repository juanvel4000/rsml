"""configuration loading for rsml"""

import dataclasses
import sqlite3
import tomllib
import typing
from pathlib import Path


@dataclasses.dataclass
class RSMLConfig:
    """holds the rsml runtime configuration"""

    subscriber_db: Path
    email_directory: Path

    server_secret: str
    posting_email: str = "dev@localhost"
    display_name: str = "rsml list"
    list_id: str = "localhost"
    archive_limit: int = 50
    archive_max: int = 100
    posting: bool = True
    posting_permissions: str = "all"
    precedence: str = "disabled"
    fix_date: bool = False

    relay_host: str = "127.0.0.1"
    relay_port: int = 25
    http_url: str = "http://127.0.0.1:8080"

    lmtp_host: str = "127.0.0.1"
    lmtp_port: int = 8024

    http_host: str = "127.0.0.1"
    http_port: int = 8080


def validate_config(
    config: RSMLConfig,
    validate_hints: bool = True,
    validate_values: bool = True,
    validate_paths: bool = False,
) -> None:
    """verify whether an RSMLConfig class is valid"""

    if validate_hints:
        hints = typing.get_type_hints(type(config))
        for field in dataclasses.fields(config):
            value = getattr(config, field.name)
            expected = hints[field.name]
            if not isinstance(value, expected):
                raise TypeError(f"{field.name} expected {expected}, got {type(value)}")

    if validate_values:
        # validate empty vars
        if not config.server_secret:
            raise ValueError("config.server_secret is empty")
        if not config.posting_email:
            raise ValueError("config.posting_email is empty")
        if not config.display_name:
            raise ValueError("config.display_name is empty")
        if not config.list_id:
            raise ValueError("config.list_id is empty")
        if config.archive_limit <= 0:
            raise ValueError("config.archive_limit must be greater than zero")
        if config.archive_max <= 0:
            raise ValueError("config.archive_max must be greater than zero")

        if config.archive_limit > config.archive_max:
            raise ValueError(
                "config.archive_limit cannot be greater than config.archive_max"
            )

        if not config.http_url:
            raise ValueError("config.http_url is empty")
        if not config.relay_host:
            raise ValueError("config.relay_host is empty")
        if not config.relay_port:
            raise ValueError("config.relay_port is empty")

        # validate vars with specific string expectations
        if config.precedence not in ["list", "disabled"]:
            raise ValueError(
                f"config.precedence expected list/disabled, got {str(config.precedence)}"
            )
        if config.posting_permissions not in ["all", "subscribers"]:
            raise ValueError(
                f"config.posting_permissions expected all/subscribers, got {str(config.posting_permissions)}"
            )

    # validate paths
    if validate_paths:
        # actual existence in fs
        if config.email_directory.exists():
            if not config.email_directory.is_dir():
                raise NotADirectoryError(config.email_directory)
        else:
            raise FileNotFoundError(config.email_directory)

        if config.subscriber_db.exists():
            if not config.subscriber_db.is_file():
                raise IsADirectoryError(config.subscriber_db)
        else:
            raise FileNotFoundError(config.subscriber_db)


def load_config(
    fil: str | Path = "./rsml.toml",
    validate: bool = True,
) -> RSMLConfig:
    """load rsml configuration from a file"""

    path = Path(fil)

    try:
        with path.open("rb") as fp:
            data = tomllib.load(fp).get("rsml", {})
            if not data:
                raise ValueError("[rsml] section is missing or empty")
    except tomllib.TOMLDecodeError as exc:
        raise ValueError(f"invalid toml in {str(path)}") from exc

    config = RSMLConfig(
        subscriber_db=Path(data.get("subscriber_db", "/var/lib/rsml/subscribers.db")),
        email_directory=Path(data.get("email_directory", "/var/lib/rsml/mail")),
        server_secret=data.get("server_secret"),
        posting_email=data.get("posting_email", "dev@localhost"),
        display_name=data.get("display_name", "rsml list"),
        list_id=data.get("list_id", "localhost"),
        archive_limit=data.get("archive_limit", 50),
        archive_max=data.get("archive_max", 100),
        posting=data.get("posting", True),
        posting_permissions=data.get("posting_permissions", "all"),
        precedence=data.get("precedence", "disabled"),
        fix_date=data.get("fix_date", False),
        relay_host=data.get("relay_host", "127.0.0.1"),
        relay_port=data.get("relay_port", 25),
        http_url=data.get("http_url", "http://127.0.0.1:8080"),
        lmtp_host=data.get("lmtp_host", "127.0.0.1"),
        lmtp_port=data.get("lmtp_port", 8024),
        http_host=data.get("http_host", "127.0.0.1"),
        http_port=data.get("http_port", 8080),
    )
    if validate:
        validate_config(config, validate_paths=False)
    return config


def build_structure(
    config: RSMLConfig, make_dirs: bool = True, make_db: bool = True
) -> None:
    validate_config(config)

    if make_dirs:
        config.email_directory.mkdir(parents=True, exist_ok=True)

    if make_db:
        config.subscriber_db.parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(config.subscriber_db) as db:
            _ = db.execute("""
                CREATE TABLE IF NOT EXISTS subscribers (
                    email TEXT PRIMARY KEY,
                    subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
                )
            """)
