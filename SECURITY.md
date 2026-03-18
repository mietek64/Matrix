# Security Policy

## Supported Versions

Only the latest release receives security updates.

| Version | Supported |
|---------|-----------|
| Latest  | ✓         |
| Older   | ✗         |

## Reporting a Vulnerability

**Please do not open a public GitHub issue for security vulnerabilities.**

Report them privately via GitHub's security advisory system:

1. Go to the [Security tab](https://github.com/mietek64/Matrix/security) of this repo
2. Click **"Report a vulnerability"**
3. Describe the issue in as much detail as possible

You'll receive a response within **72 hours**. Confirmed vulnerabilities will be
patched as soon as possible and credited in the release notes (unless you prefer
to remain anonymous).

## Scope & Threat Model

Matrix is a personal terminal animation tool. It:

- **Makes no network connections** at runtime
- **Has no authentication**, user accounts, or data storage beyond a local JSON config file
- **Reads one local file** (`config.json`) using Python's standard `json` module — no `eval`, no exec
- **Writes one local file** when the user explicitly saves from the config editor

Realistic attack surface is limited to:

| Surface | Notes |
|---------|-------|
| Malicious `-f` config file | Parser uses stdlib `json` only — malformed input is rejected gracefully, no code execution possible |
| Supply chain | Runtime dependencies are `rich` and `pyfiglet` — both well-maintained, widely used PyPI packages |
| Pre-built binary | Built with PyInstaller from the source in this repo — you can verify by building it yourself |

## Pre-built Binary Verification

The `.exe` and Linux binaries in Releases are built directly from `matrix.py` in this repository
using PyInstaller. To verify:

1. Clone the repo
2. Follow the [Build from Source](README.md#build-from-source) instructions
3. Compare the output binary with the one from Releases

## Note on Antivirus False Positives

Windows Defender and some antivirus tools may flag the `.exe` as suspicious.
This is a known and widely-documented false positive caused by PyInstaller's bootloader,
not by anything in the code. The full source is available for inspection above.
