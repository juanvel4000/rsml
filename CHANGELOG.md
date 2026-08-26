# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/2.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `quick start` section to `README.md`
- github workflow to push container images to ghcr
- `Containerfile`, `compose.yaml`, and `.containerignore` files for containers
- add redis support in rate limiter (`http.py`)
- add config file fallback system (`cli.py`)

## [0.2.1] - 2026-08-24

### Fixed

- update verify tests for GET/POST split (`test_http.py`)
- validate specified dates in `GET /list/archive` (`http.py`)
- reject non-positive `limit` in `GET /list/archive` (`http.py`)
- escape email addresses in `mailer.py` URLs

## [0.2.0] - 2026-08-24

### Added

- add rate-limiting to `POST /list/subscribe` (`http.py`)
- allow using `rsml-http` and `rsml-lmtp` as separate entrypoints in `cli.py`

### Fixed

- do not request upload permissions in `tests.yml`
- fix the validation order on `/list/archive` (`http.py`)
- fix the `[:limit]` slice bug in `/list/archive` (`http.py`)

### Changed

- isolated per-recipient failure in `Mailer.forward_message` (`mailer.py`)
- use a single sqlite3 instance across the `Storage` class (`storage.py`)
- improved subscription verification handling (`http.py`)

## [0.1.5] - 2026-08-23

### Added

- `CONTRIBUTING.md` guidelines

### Fixed

- fixed minor issues across various files in the codebase
- rename `publish` to `tests` in `tests.yml:jobs`

## [0.1.4] - 2026-08-23

### Added

- github actions workflow for tests (`tests.yml`)

## [0.1.3] - 2026-08-23

### Added

- badges on README.md
- `publish.yml` workflow via github actions

## [0.1.2] - 2026-08-23

### Added

- other metadata to `pyproject.toml`

## [0.1.1] - 2026-08-23

### Added

- readme entry in `pyproject.toml`

### Changed

- `__init__.py` as the single source of truth for project versioning

## [0.1.0] - 2026-08-23

### Added

- toml-based configuration (`rsml.toml`) (`rsml.config`)
- unit test suite (`tests/`)
- RFC 4155 and mboxrd compliant `.mbox` file generator (`rsml.mbox`)
- HMAC-SHA256 token generation for verify/unsub links (`rsml.tokens`)
- mailing list posting via LMTP, with `all` / `subscribers` permission mode
- two-step subscription via `/list/subscribe` and `/list/verify`
- `/list/archive` endpoint for `.mbox` archive retrieval of the mailing list
- one-click unsubscribe with `List-Unsubscribe` and `List-Unsubscribe-Post` (RFC 8058)
- project spec (`SPEC.md`)
