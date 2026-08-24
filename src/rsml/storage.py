""".eml files and subscriber database manager for rsml"""

import secrets
import sqlite3
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from .config import RSMLConfig, build_structure, validate_config


class Storage:
    def __init__(self, config: RSMLConfig):
        self.config = config

        validate_config(config)
        build_structure(config)
        self.db = sqlite3.connect(config.subscriber_db, check_same_thread=False)

    def store_message(self, message: bytes) -> Path:
        """store the message in a file"""
        now = datetime.now(UTC)
        date = now.strftime("%Y/%m/%d")
        uid = secrets.token_hex(8)

        path = self.config.email_directory / date / f"{uid}.eml"
        path.parent.mkdir(exist_ok=True, parents=True)

        _ = path.write_bytes(message)

        return path

    def get_message(self, path: Path) -> bytes:
        """read a stored message"""
        return path.read_bytes()

    def iter_messages(
        self,
        year: int | Literal["all"] = "all",
        month: int | Literal["all"] = "all",
        day: int | Literal["all"] = "all",
    ) -> Iterator[Path]:
        """iterate through messages from a specific date"""
        globstr = ""
        if year == "all":
            globstr += "*/"
        else:
            globstr += f"{year}/"

        if month == "all":
            globstr += "*/"
        else:
            globstr += f"{month:02d}/"

        if day == "all":
            globstr += "*/"
        else:
            globstr += f"{day:02d}/"

        globstr += "*.eml"
        yield from self.config.email_directory.glob(globstr)

    def add_subscriber(self, email: str) -> bool:
        _ = self.db.execute(
            "INSERT OR IGNORE INTO subscribers (email) VALUES (?)", (email,)
        )

        self.db.commit()
        return True

    def remove_subscriber(self, email: str) -> bool:
        _ = self.db.execute("DELETE FROM subscribers WHERE email = ?", (email,))
        self.db.commit()
        return True

    def is_subscribed(self, email: str) -> bool:
        row = self.db.execute(
            "SELECT 1 FROM subscribers WHERE email = ?", (email,)
        ).fetchone()
        return row is not None

    def get_subscribers(self) -> Iterator[str]:
        rows = self.db.execute("SELECT email FROM subscribers")
        for (email,) in rows:
            yield email

    def close(self) -> None:
        self.db.close()

    def __repr__(self) -> str:
        return f"Storage(config={self.config})"
