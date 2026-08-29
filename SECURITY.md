# security policy

## supported versions

only the latest released version of rsml is supported with security fixes

## reporting a vulnerability

**do not** open a public github issue for security vulnerabilities.

instead, use github's private [vulnerability reporting](https://github.com/juanvel4000/rsml/security/advisories/new) section.

include steps to reproduce and impact if known. the patch will be reviewed and aim to patch within a few days before public disclosure.

## scope

### in scope

- rsml and modules (`http.py`, `mailer.py`, `cli.py`, `lmtp.py`, `mbox.py`, `storage.py`, `tokens.py`, `config.py`)

### out of scope

- misconfigured `rsml.toml`
- mta used
- reverse proxy (if any)
