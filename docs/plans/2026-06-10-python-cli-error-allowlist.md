# Python CLI Error Allowlist

Status: Completed

## Goal

Prevent provider or dependency exceptions from leaking diagnostics merely
because they use Python's common `RuntimeError` or `ValueError` types.

## Implementation

- Raise sample-owned message and credential validation exception subclasses.
- Allowlist only those custom exception types for detailed CLI output.
- Return a generic failure for every other exception message.
- Exercise provider `RuntimeError` and `ValueError` redaction paths.
- Extend the scripted baseline with source and regression-test contracts.

## Verification

- `make check`
- Mutation check: restoring exception-type-based disclosure must fail the
  provider `RuntimeError` regression test.
