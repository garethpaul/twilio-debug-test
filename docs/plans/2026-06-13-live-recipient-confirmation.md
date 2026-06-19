# Live Recipient Confirmation

## Status: Completed

## Context

The samples are dry-run safe by default, but enabling `TWILIO_SEND_LIVE=true`
immediately sends to the configured `TWILIO_TO` value. A stale or mistyped
recipient can therefore receive a real message after one environment switch.

## Requirements

- R1. Require `TWILIO_CONFIRM_TO` for live sends in both Python and Node.js.
- R2. Normalize and validate the confirmation as E.164, then require it to
  exactly match the normalized message recipient.
- R3. Reject missing, malformed, or mismatched confirmation before importing
  the Twilio SDK or constructing a client.
- R4. Preserve dry-run behavior without requiring credentials or confirmation.
- R5. Surface sample-owned confirmation errors through the existing safe CLI
  validation path without exposing provider details or credentials.
- R6. Preserve explicit message overrides, body bounds, credential checks,
  logging controls, SID redaction, and runtime-matrix CI.
- R7. Tests and baseline contracts must reject missing or reordered
  confirmation safeguards in both runtimes.

## Scope Boundaries

- Do not make a live Twilio request or validate provider-side authorization.
- Do not add dependencies, retries, persistence, or an interactive prompt.
- Do not change dry-run output or support non-E.164 recipient types.

## Implementation Units

### U1. Add shared live-recipient validation

- **Files:** `test.py`, `test.js`
- Validate `TWILIO_CONFIRM_TO` only after live mode is selected and before any
  credential import/client setup.

### U2. Add fail-closed regression coverage

- **Files:** `tests/test_company_comms.py`, `tests/test_js_contracts.js`
- Cover missing, malformed, mismatched, whitespace-normalized matching, client
  setup ordering, dry-run independence, and safe CLI messages.

### U3. Preserve repository contracts and guidance

- **Files:** `scripts/check-baseline.sh`, `tests/test_docs_plans.py`,
  `README.md`, `SECURITY.md`, `VISION.md`, `CHANGES.md`
- Enforce both implementations and document the two-step live-send boundary.

## Verification

- `python3 -m unittest discover -s tests -p 'test_company_comms.py'`
  passed 26 tests.
- `node tests/test_js_contracts.js` passed.
- `make check` passed locally, from an external working directory, and from a
  copied repository path containing spaces. Each run passed 28 Python tests,
  the Node.js contract suite, and the scripted baseline.
- Eight hostile mutations covering removed calls, weakened matching, removed
  E.164 checks, dry-run regression, and stale plan status were all rejected.
- Workflow YAML, shell syntax, `git diff --check`, generated-artifact, and
  focused secret reviews are included in final validation.
