# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/2.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
