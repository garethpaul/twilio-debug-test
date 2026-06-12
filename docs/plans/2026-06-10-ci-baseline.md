# Hosted CI Baseline

Status: Completed

## Context

The repository had local Python and Node.js `make check` verification for the
Twilio debug samples, but no hosted workflow protected dry-run safety, live-send
opt-in, validation, redaction, or maintenance contracts on pushes and pull
requests.

## Changes

- Added an Ubuntu 24.04 GitHub Actions matrix pairing Python 3.10, 3.12, and
  3.14 with Node.js 20, 22, and 24.
- Pinned checkout, Python setup, and Node.js setup actions by full commit SHA.
- Restricted permissions to read-only contents, disabled checkout credential
  persistence, bounded jobs to ten minutes, and cancelled superseded runs.
- Kept push and pull-request coverage unfiltered so remediation branches receive
  the same hosted signal as the default branch.
- Ran `make check` from both the repository and a temporary working directory in
  each matrix job.
- Extended the baseline guard and docs so the exact hosted contract and this
  completed plan remain checked in.

## Verification

- `make check`
- `make verify`
- external-working-directory `make check`
- hostile workflow mutation checks
- `git diff --check`
