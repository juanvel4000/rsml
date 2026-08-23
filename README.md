# rsml

![PyPI License](https://img.shields.io/pypi/l/rsml)
![PyPI Status](https://img.shields.io/pypi/status/rsml)
![PyPI Version](https://img.shields.io/pypi/v/rsml)
![GitHub Actions Workflow Status (Publish)](https://img.shields.io/github/actions/workflow/status/juanvel4000/rsml/publish.yml?label=publish)
![GitHub Actions Workflow Status (Tests)](https://img.shields.io/github/actions/workflow/status/juanvel4000/rsml/tests.yml?label=tests)

a small, self-hosted mailing list system.

**rsml** is a **m**ailing **l**ist **m**anager system written in python built with minimalism in mind, it does not try to be a GNU Mailman competitor but rather a simpler alternative.

## features

- toml-based configuration (`rsml.toml`) (`rsml.config`)
- RFC 4155 and mboxrd compliant `.mbox` file generator (`rsml.mbox`)
- mailing list posting via LMTP
- two-step subscription via `/list/subscribe` and `/list/verify`
- `/list/archive` endpoint for `.mbox` archive retrieval of the mailing list
- one-click unsubscribe with `List-Unsubscribe` and `List-Unsubscribe-Post` (RFC 8058)

## dependencies

rsml requires at least

- a python `>=3.11`-compatible interpreter
- an MTA capable of receiving and sending mail through SMTP and LMTP

runtime dependencies include

- `aiosmtpd`/`aiosmtplib`: for asynchronous SMTP/LMTP operations
- `flask`: for the http server
- `email-validator`: to validate email addresses

development-time dependencies include:

- `pytest`/`pytest-asyncio`: to execute the unit tests

## usage

```sh
  $ pip install -e . # install rsml and dependencies
  $ cp rsml.toml.example rsml.toml # edit server_secret, etc.
  $ rsml http # start the http server
  $ rsml lmtp # start the lmtp server
```

running the test suite can be done with `pytest`

```sh
  $ pip install -e ".[dev]" # install dev dependencies
  $ pytest -vs . # run the unit tests
```

## spec

a document outlining the technical specifications of the project can be found in this repository as [SPEC.md](SPEC.md)

## license

BSD-3-Clause, see [LICENSE](LICENSE)
