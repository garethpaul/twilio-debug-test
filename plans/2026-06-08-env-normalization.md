# Environment Normalization Gate

## Problem

Both Twilio samples read message settings and live-send flags directly from
environment values. Whitespace-padded phone numbers, message bodies, or
`TWILIO_SEND_LIVE` flags could change redaction, body length reporting, or
live-send opt-in behavior.

## TDD Evidence

1. Added Python and Node.js tests for trimmed message settings, blank message
   bodies, and whitespace-tolerant live-send flags.
2. Ran the focused test commands before implementation and confirmed the new
   tests failed in both languages.
3. Added small normalization helpers to both samples and reran the full
   verification gate.

## Verification

- `make lint`
- `python3 -m unittest discover -s tests -p 'test_*.py'`
- `node tests/test_js_contracts.js`
- `make test`
- `make verify`
- `make check`
- `git diff --check`
