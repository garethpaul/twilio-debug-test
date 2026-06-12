# E.164 Phone Validation

## Status: Completed

## Context

The Python and Node samples trim message settings and reject missing values,
but accept arbitrary nonblank sender and recipient strings. Malformed values
can therefore appear valid in dry-run output and reach the live Twilio client.

## Objectives

- Require `TWILIO_TO` and `TWILIO_FROM` to use a conservative E.164 shape.
- Keep Python and Node behavior and error wording aligned.
- Preserve message-body limits, dry-run privacy, live-send opt-in, credential
  validation, provider-error redaction, and explicit override precedence.
- Cover valid boundaries, malformed values, and CLI-safe errors.

## Contract

- A phone value must start with `+`.
- The first digit after `+` must be 1-9.
- The value must contain 2-15 digits total after `+`.
- Whitespace is trimmed before validation; internal whitespace, punctuation,
  extensions, and non-ASCII digits are rejected.

## Verification

- Focused Python discovery passed 20 communication tests; the full repository
  gate passed 22 Python tests and the Node contract suite.
- Boundary coverage accepts `+12` and a 15-digit value; malformed coverage
  rejects missing plus signs, leading-zero country codes, internal whitespace,
  punctuation, extensions, non-ASCII digits, and overlength values for both
  sender and recipient fields.
- `make check` passed locally and through `make -C` from `/tmp`.
- Five hostile mutations weakening the Python or Node regex/call sites or the
  completed plan were rejected.
- Python and Node syntax checks, the scripted baseline, and `git diff --check`
  passed.
