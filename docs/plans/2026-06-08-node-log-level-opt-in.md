# Node Log Level Opt-In

## Status: Completed

## Context

The samples dry-run by default and require `TWILIO_SEND_LIVE=true` for live
sends, but the Node.js live-send path still defaulted the Twilio client log
level to `debug`. Debug logs are useful for troubleshooting, but they can expose
phone numbers, request metadata, and message context if shared without review.

## Objectives

- Preserve the Node.js Twilio debug sample.
- Default live-send logging to `info`.
- Keep `TWILIO_LOG_LEVEL=debug` available as an explicit opt-in.
- Normalize and constrain supported log level values.
- Cover the live-send log-level assignment in Node.js tests.

## Work Completed

- Added `twilioLogLevel()` with trimming, lowercasing, and supported-level
  fallback behavior.
- Changed the live-send client assignment to use `twilioLogLevel(env)`.
- Exported and tested the helper, including explicit `debug` opt-in.
- Updated README, VISION, and CHANGES.

## Verification

- `python3 -m unittest discover -s tests -p 'test_*.py'`
- `node tests/test_js_contracts.js`
- `make check`
- `make verify`
- `git diff --check`

## Follow-Up Candidates

- Add mocked Twilio client examples for local live-send development.
- Add concrete redaction examples for debug logs before sharing them.
