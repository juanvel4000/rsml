"""functions for the cli frontend"""

import os
import signal
import sys

from .config import RSMLConfig, load_config
from .http import create_app
from .lmtp import controller_init


def run_http(config: RSMLConfig):
    """initialize the http server"""
    print("rsml http server")
    print(f"> listening on {config.http_host}:{config.http_port}")
    app = create_app(config)
    app.run(host=config.http_host, port=config.http_port)


def run_lmtp(config: RSMLConfig):
    """initialize the lmtp server"""
    print("rsml lmtp server")
    print(f"> listening on {config.lmtp_host}:{config.lmtp_port}")
    controller = controller_init(config)
    try:
        signal.pause()
    except KeyboardInterrupt:
        pass
    finally:
        controller.stop()


def print_usage() -> None:
    """print usage string"""
    print("usage: rsml <command>")


def print_help() -> None:
    """print help message"""
    print_usage()
    print("really simple mailing lists")
    print("tiny mlm implementation")
    print("commands:")
    print("  http   starts the rsml http server")
    print("  lmtp   starts the rsml lmtp server")
    print("  help   show this message")
    print("licensed under BSD-3-Clause")
    print("RSML_CONFIG= env variable to specify a config file, defaults to ./rsml.toml")


def main():
    argv = sys.argv
    argc = len(argv)

    if argc <= 1:
        print_usage()
        sys.exit(1)

    match argv[1]:
        case "http":
            config = load_config(os.getenv("RSML_CONFIG", "rsml.toml"))
            run_http(config)
            sys.exit(0)
        case "lmtp":
            config = load_config(os.getenv("RSML_CONFIG", "rsml.toml"))
            run_lmtp(config)
            sys.exit(0)
        case "help":
            print_help()
            sys.exit(0)
        case _:
            print(f"unknown command: {argv[1]}")
            print_usage()
            sys.exit(1)
