"""functions for the cli frontend"""

import os
import signal
import sys
from pathlib import Path

from .config import RSMLConfig, load_config
from .http import create_app
from .lmtp import controller_init, controller_stop


def run_http(config: RSMLConfig):
    """initialize the http server"""
    print("rsml http server")
    print(f"> listening on {config.http_host}:{config.http_port}")
    app = create_app(config)
    try:
        app.run(host=config.http_host, port=config.http_port)
    finally:
        app.config["RSML_STORAGE"].close()


def run_lmtp(config: RSMLConfig):
    """initialize the lmtp server"""
    print("rsml lmtp server")
    print(f"> listening on {config.lmtp_host}:{config.lmtp_port}")
    controller, storage = controller_init(config)
    try:
        signal.pause()
    except KeyboardInterrupt:
        pass
    finally:
        controller_stop(controller, storage)


def print_usage() -> None:
    """print usage string"""
    print("usage: rsml <command>")


def print_help() -> None:
    """print help message"""
    print_usage()
    print("really simple mailing lists (rsml)")
    print("a small, self-hosted mailing list system.")
    print("commands:")
    print("  http   starts the rsml http server")
    print("  lmtp   starts the rsml lmtp server")
    print("  help   show this message")
    print("licensed under BSD-3-Clause")


def get_config() -> RSMLConfig:
    env_path = os.getenv("RSML_CONFIG")
    if env_path:
        try:
            return load_config(Path(env_path))
        except Exception:
            pass

    options = [
        Path("./rsml.toml"),
        Path("~/.rsml.toml").expanduser(),
        Path("~/.config/rsml/rsml.toml").expanduser(),
        Path("~/.rsml/rsml.toml").expanduser(),
        Path("/etc/rsml.toml"),
        Path("/etc/rsml.d/rsml.toml"),
    ]

    for fil in options:
        if fil.is_file():
            try:
                return load_config(fil)
            except Exception:
                continue

    print("could not find a valid rsml.toml")
    sys.exit(1)


def main():
    argv = sys.argv
    argc = len(argv)

    match os.path.basename(argv[0]):
        case "rsml-http":
            config = get_config()
            run_http(config)
            sys.exit(0)
        case "rsml-lmtp":
            config = get_config()
            run_lmtp(config)
            sys.exit(0)

        case _:
            pass

    if argc <= 1:
        print_usage()
        sys.exit(1)

    match argv[1]:
        case "http":
            config = get_config()
            run_http(config)
            sys.exit(0)
        case "lmtp":
            config = get_config()
            run_lmtp(config)
            sys.exit(0)
        case "help":
            print_help()
            sys.exit(0)
        case _:
            print(f"unknown command: {argv[1]}")
            print_usage()
            sys.exit(1)
