# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/2.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- toml-based configuration (`rsml.toml`) (`rsml.config`)
- unit test suite (`tests/`)
- RFC 4155 and mboxrd compliant `.mbox` file generator (`rsml.mbox`)
- HMAC-SHA256 token generation for verify/unsub links (`rsml.tokens`)
- mailing list posting via LMTP, with `all` / `subscribers` permission mode
- two-step subscription via `/list/subscribe` and `/list/verify`
- `/list/archive` endpoint for `.mbox` archive retrieval of the mailing list
- one-click unsubscribe with `List-Unsubscribe` and `List-Unsubscribe-Post` (RFC 8058)
