# really simple mailing lists

![pypi license](https://img.shields.io/pypi/l/rsml)
![pypi status](https://img.shields.io/pypi/status/rsml)
![pypi version](https://img.shields.io/pypi/v/rsml)
![github actions workflow status (publish)](https://img.shields.io/github/actions/workflow/status/juanvel4000/rsml/publish.yml?label=publish)
![github actions workflow status (tests)](https://img.shields.io/github/actions/workflow/status/juanvel4000/rsml/tests.yml?label=tests)
![github actions workflow status (ghcr push)](https://img.shields.io/github/actions/workflow/status/juanvel4000/rsml/ghcr-push.yml?label=ghcr-push)

a small, self-hosted mailing list system.

**rsml** is a **m**ailing **l**ist **m**anager system written in python built with minimalism in mind, it does not try to be a GNU Mailman competitor but rather a simpler alternative.

## features

- toml-based configuration (`rsml.toml`) (`rsml.config`)
- RFC 4155 and mboxrd compliant `.mbox` file generator (`rsml.mbox`)
- mailing list posting via LMTP
- two-step subscription via `/list/subscribe` and `/list/verify`
- `/list/archive` endpoint for `.mbox` archive retrieval of the mailing list
- one-click unsubscribe with `List-Unsubscribe` and `List-Unsubscribe-Post` (RFC 8058)

## quick start

rsml can be run directly with python or as a container using an OCI-compatible runtime.

1. create a configuration

```sh
cp rsml.toml.example rsml.toml # copy the example configuration
${EDITOR:-nano} rsml.toml # modify the configuration file
```

> at minimum, configure the server secret. see `rsml.toml.example` for the available options.

2. run rsml

2.1 with python

```sh
pip install rsml # install rsml and dependencies
```

start the http server:

```sh
rsml http
```

in a separate process, start the lmtp server:

```sh
rsml lmtp
```

2.2 with a container

alternatively, rsml can be run from its OCI container image using podman, docker, or another OCI-compatible runtime.

example (with podman)

```sh
podman run --rm -it \
  -p 8080:8080 \
  -v "$PWD/rsml.toml:/home/rsml/rsml.toml:ro" \
  ghcr.io/juanvel4000/rsml:latest \
  http
```

and for the lmtp server

```sh
podman run --rm -it \
  -p 8024:8024 \
  -v "$PWD/rsml.toml:/home/rsml/rsml.toml:ro" \
  ghcr.io/juanvel4000/rsml:latest \
  lmtp
```

3. configure your mta

rsml receives mailing-list messages through LMTP. configure your mta to deliver messages destined for the mailing list to the rsml lmtp server.

set `relay_host` and `relay_port` in `rsml.toml` to the hostname and port of the mta used by rsml for outgoing mail.

## dependencies

rsml requires at least

- a python `>=3.11`-compatible interpreter

a complete deployement requires

- an mta capable of receiving mail and delivering messages to rsml over LMTP

runtime dependencies include

- `aiosmtpd`/`aiosmtplib`: for asynchronous SMTP/LMTP operations
- `flask`: for the http server
- `email-validator`: to validate email addresses

development-time dependencies include:

- `pytest`/`pytest-asyncio`: to execute the unit tests

## usage

```sh
pip install -e . # install rsml and dependencies
cp rsml.toml.example rsml.toml # edit server_secret, etc.
rsml http # start the http server
rsml lmtp # start the lmtp server
```

running the test suite can be done with `pytest`

```sh
pip install -e ".[dev]" # install dev dependencies
pytest -vs . # run the unit tests
```

redis support for the rate limiter requires the `redis` optional dependency set to be installed

```sh
pip install -e ".[redis]"
```

## spec

a document outlining the technical specifications of the project can be found in this repository as [SPEC.md](SPEC.md)

## project status

rsml is in active development. while functional, it is **not yet production-ready** for real-world usage.

- [CHANGELOG.md](CHANGELOG.md) -- release history
- [CONTRIBUTING.md](CONTRIBUTING.md) -- how to report bugs and send patches

## license

BSD-3-Clause -- see [LICENSE](LICENSE)
