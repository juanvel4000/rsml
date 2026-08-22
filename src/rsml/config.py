"""configuration loading for rsml"""

from pathlib import Path
import tomllib
import dataclasses
import typing

@dataclasses.dataclass
class RSMLConfig:
    """holds the rsml runtime configuration"""

    server_secret: str | None = None
    posting_email: str = "dev@localhost"
    display_name: str = "rsml list"
    list_id: str = "localhost"
    archive_limit: int = 50
    archive_max: int = 100
    posting: bool = True
    posting_permissions: str = "all"
    subscriber_db: Path | None = None
    email_directory: Path | None = None
    precedence: str = "disabled"
    fix_date: bool = False

def validate_config(config: RSMLConfig, validate_hints: bool = True, validate_values: bool = True, validate_paths: bool = False) -> bool:
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

        # validate vars with specific string expectations
        if config.precedence not in ["list", "disabled"]:
            raise ValueError(f"config.precedence expected list/disabled, got {str(config.precedence)}")
        if config.posting_permissions not in ["all", "subscribers"]:
            raise ValueError(f"config.posting_permissions expected all/subscribers, got {str(config.posting_permissions)}")

    # validate paths
    if validate_paths:
        # variable check
        if not config.email_directory:
            raise ValueError("config.email_directory is empty")
        if not config.subscriber_db:
            raise ValueError("config.subscriber_db is empty")

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

    return True
