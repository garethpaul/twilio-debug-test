# Python Log Level Opt-In

## Status: Completed

## Context

The Node.js sample defaulted live-send logging to `info` and allowed an
explicit `TWILIO_LOG_LEVEL` opt-in. The Python sample also set Twilio client
logging to `info`, but it did not share the same supported opt-in path or tests.

## Objectives

- Preserve dry-run-by-default behavior for both language samples.
- Keep Python live-send logging at `info` unless explicitly configured.
- Allow only known `TWILIO_LOG_LEVEL` values.
- Cover Python live-send logging with a fake Twilio client instead of live API
  calls.

## Work Completed

- Added `twilio_log_level()` and supported Python logging-level mappings.
- Wired Python live sends to `TWILIO_LOG_LEVEL` with `info` fallback.
- Added fake-client tests for default Python logging and supported opt-in
  values.
- Updated README, VISION, and CHANGES.

## Verification

- `python3 -m unittest discover -s tests -p 'test_*.py'`
- `node tests/test_js_contracts.js`
- `make check`
- `make verify`
- `git diff --check`

## Follow-Up Candidates

- Add language-specific dependency manifests.
- Add mocked Twilio client examples for local live-send development.
