# Provider Request Timeout

## Status: Planned

## Priority

1. Bound Python live Twilio requests that currently use an unbounded default
   HTTP timeout.
2. Make the existing Node timeout expectation explicit so dependency upgrades
   cannot silently change it.
3. Preserve dry-run behavior, validation ordering, redacted CLI output, and
   injected fake-client support.
4. Do not add automatic retries that could duplicate message creation.

## Context

The Python live-send path constructs Twilio's default synchronous client, whose
underlying HTTP client currently receives `timeout=None`. A stalled provider or
network path can therefore hold the command indefinitely at the local client
layer. The Node helper currently defaults to a 30-second socket timeout, but the
sample does not state or test that bound.

## Scope

- Add shared language-local constants for a 30-second provider request timeout
  in `test.py` and `test.js`.
- Construct the default Python Twilio client with a `TwilioHttpClient` carrying
  that timeout while preserving two-argument injected client factories.
- Pass an explicit 30,000-millisecond timeout through the Node client factory.
- Add focused mocked contracts in `tests/test_company_comms.py` and
  `tests/test_js_contracts.js` that prove the timeout reaches the client without
  making live requests.
- Extend `tests/test_docs_plans.py`, `README.md`, `SECURITY.md`, `VISION.md`, and
  `CHANGES.md` with the provider request-timeout boundary.

## Acceptance Criteria

- Python's default live client uses a 30-second `TwilioHttpClient` timeout.
- Node client construction receives `{ timeout: 30000 }`.
- Injected Python fake factories remain callable with account SID and auth token
  only; Node fake factories receive and can assert the options object.
- Dry-run mode never imports or creates a Twilio client.
- Provider errors remain sanitized by the existing CLI allowlist.
- No retry is enabled by either implementation.

## Verification Plan

- Run focused Python and Node tests for client construction and live-send
  behavior.
- Run `make check` from the repository and through the absolute Makefile path
  from an external directory using isolated pinned dependencies.
- Prove hostile mutations removing or changing either timeout are rejected.
- Audit the exact diff, generated artifacts, dependency outputs, credential
  paths, changed lines for secret-like values, and package vulnerabilities.
- Capture one bounded exact-head hosted check, CodeQL, and alert snapshot after
  push.

## Verification

Pending implementation and validation.

## Scope Boundary

This change does not call Twilio, validate provider credentials, confirm real
delivery, add automatic retries, introduce message idempotency, or change the
existing recipient-confirmation and dry-run safety model.
