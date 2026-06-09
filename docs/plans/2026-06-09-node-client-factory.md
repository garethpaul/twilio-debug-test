# Node Client Factory

## Status: Completed

## Context

The Python sample already accepts a fake Twilio client factory so live-send
behavior can be tested without importing Twilio or reaching the network. The
Node.js sample only required Twilio at runtime, which left its live-send payload
and log-level assignment covered by string checks rather than an executable
fake-client path.

## Objectives

- Preserve the default Node.js behavior of requiring `twilio` for real live
  sends.
- Allow tests to inject a fake Twilio client factory.
- Cover live-send credentials, payload, message SID, and log-level assignment
  without live credentials or network calls.
- Keep dry-run behavior unchanged.

## Work Completed

- Added an optional `clientFactory` argument to `sendMessage()`.
- Kept `require('twilio')` as the default factory when no fake is supplied.
- Extended `tests/test_js_contracts.js` with a fake client live-send path.
- Updated README, VISION, and CHANGES.

## Verification

- `node --check test.js`
- `node --check tests/test_js_contracts.js`
- `node tests/test_js_contracts.js`
- `python3 -m unittest discover -s tests -p 'test_*.py'`
- `make lint`
- `make test`
- `make build`
- `make check`
- `make verify`
- `git diff --check`

## Follow-Up Candidates

- Add language-specific dependency manifests for easier setup.
- Add deeper redaction examples for shared debug logs.
