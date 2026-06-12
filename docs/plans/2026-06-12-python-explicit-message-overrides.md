# Python Explicit Message Overrides

Status: Completed

## Context

The Python helper chooses each message field with `explicit or environment`.
An explicitly supplied blank recipient, sender, or body therefore falls back to
the corresponding environment default instead of failing validation.

## Priority

Silent fallback is unsafe for a live-send helper because a caller attempting to
clear or replace a recipient can send to a previously configured environment
destination. Explicit input must take precedence even when it is invalid.

## Prioritized Backlog

1. Fall back to environment message settings only when an argument is omitted.
2. Reject explicit blank values before dry-run output or Twilio client setup.
3. Keep broader phone-address format validation separate because Twilio also
   supports non-E.164 sender and channel address forms.

## Implementation

- Add a small message-setting helper that distinguishes `None` from blank text.
- Read an environment fallback only when its corresponding argument is omitted.
- Preserve trimming for both explicit and environment values.
- Add regressions for blank recipient, sender, and body overrides.
- Assert that invalid explicit values never construct the injected client.
- Extend the baseline and operational documentation.

## Verification

- `python3 -m unittest discover -s tests -p 'test_*.py'`
- `node tests/test_js_contracts.js`
- `make lint`
- `make test`
- `make build`
- `make check`
- `git diff --check`
- Mutations restoring truthy fallback for explicit blanks must fail.
- A failing environment mapping is not consulted for complete explicit input.
