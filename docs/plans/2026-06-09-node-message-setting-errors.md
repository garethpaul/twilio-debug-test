# Node Message Setting Errors

## Status: Completed

## Context

The Node.js sample already reports all missing live-send credential names
together before constructing a Twilio client. Its message payload validation
still failed one field at a time, so an empty CLI environment reported only
`TWILIO_FROM` even though `TWILIO_TO` and `TWILIO_BODY` were also missing.

## Objectives

- Report all missing Node.js message setting names in one concise error.
- Keep required settings trimmed before payload creation.
- Preserve dry-run behavior and live-send credential validation.
- Cover the behavior through the exported Node.js CLI runner.
- Keep the completed plan required by `make check`.

## Work Completed

- Changed `createMessagePayload()` to reuse grouped setting validation for
  `TWILIO_FROM`, `TWILIO_TO`, and `TWILIO_BODY`.
- Kept payload values normalized with `settingValue()` after validation.
- Updated Node.js contract tests for combined message-setting errors.
- Updated docs-plan tests to require this completed plan.
- Updated README, VISION, and CHANGES.

## Verification

- Negative check before implementation:
  `node tests/test_js_contracts.js` failed because Node reported only
  `Missing required Twilio setting: TWILIO_FROM`.
- `node --check test.js`
- `node --check tests/test_js_contracts.js`
- `node tests/test_js_contracts.js`
- `python3 -m unittest discover -s tests -p 'test_*.py'`
- `make check`
- `git diff --check`

## Follow-Up Candidates

- Add language-specific dependency manifests.
- Add deeper redaction examples for shared debug logs.
