---
title: "fix: Validate Twilio credential shapes before client setup"
type: fix
date: 2026-06-13
---

# Validate Twilio Credential Shapes Before Client Setup

## Status: Completed

## Context

Live mode rejects missing Twilio credentials, but malformed Account SIDs and
auth tokens still reach SDK client construction. That delays a deterministic
configuration error until provider setup or request time and can expose more
provider-controlled diagnostics than necessary.

## Requirements

- R1. Require Account SIDs to use the `AC` prefix followed by 32 hexadecimal
  characters.
- R2. Require auth tokens to contain exactly 32 hexadecimal characters.
- R3. Apply matching validation in Python and Node.js before client factories
  are invoked.
- R4. Preserve dry-run behavior without requiring credentials.
- R5. Route malformed credentials through the existing sample-owned credential
  error type and safe CLI output.
- R6. Add boundary, case, ordering, and mutation-resistant coverage.

## Scope Boundaries

This change validates only the canonical Twilio credential shapes. It does not
verify credentials with Twilio, send a live message, validate API keys, or
change the explicit debug-log opt-in.

## Implementation Units

### U1. Validate Live Credential Shapes

- **Goal:** Fail locally before either SDK client is constructed.
- **Files:** `test.py`, `test.js`
- **Approach:** Add anchored ASCII hexadecimal patterns and shared credential
  validators. Run them after missing-setting checks and before client factory
  calls in both implementations.
- **Test scenarios:** Lowercase and uppercase hexadecimal credentials pass;
  wrong prefix, short, long, and non-hex values fail; dry run ignores malformed
  credential values; factories are not invoked on failure.
- **Verification:** Python and Node behavior remains aligned.

### U2. Add Cross-Runtime Contracts

- **Goal:** Prevent validation removal or ordering drift.
- **Files:** `tests/test_company_comms.py`, `tests/test_js_contracts.js`,
  `scripts/check-baseline.sh`
- **Approach:** Add focused fake-client tests and static contracts requiring
  patterns, validators, boundary cases, and validation before factory setup.
- **Test scenarios:** Mutations remove either runtime validator, weaken hex or
  length requirements, move validation after setup, or remove boundary tests.
- **Verification:** Full Python/Node gates and hostile mutations reject each
  weakened contract.

### U3. Document the Credential Boundary

- **Goal:** Record the local validation behavior without implying that shape
  validation proves credentials are active.
- **Files:** `README.md`, `SECURITY.md`, `VISION.md`, `CHANGES.md`,
  `docs/plans/2026-06-13-twilio-credential-shapes.md`
- **Approach:** Document accepted shapes, fail-fast ordering, and the absence of
  live provider verification.
- **Test expectation:** Documentation remains part of the scripted baseline.
- **Verification:** The completed plan records actual commands and results.

## Risks

- Patterns that accept non-ASCII hexadecimal characters would weaken the gate.
- Requiring credentials in dry-run mode would break the repository's safe
  default.
- Shape validation cannot establish that a credential is current or authorized.

## Assumptions

- This sample uses Account SID plus auth token credentials, not Twilio API key
  credentials with `SK` identifiers.

## Verification

- `python3 -m unittest discover -s tests -p 'test_company_comms.py'`: passed 23
  focused Python tests.
- `node tests/test_js_contracts.js`: passed the Node.js contract suite.
- `/tmp/engineering-bar/mutate-twilio-credential-shapes.sh`: rejected six
  Account SID length, auth-token length, and skipped-validation mutations across
  Python and Node.js.
- `git diff --check`: passed.
- `make check`: passed Python compilation, Node.js syntax checks, 25 Python
  tests, the Node.js contract suite, and the scripted baseline.
- `make -C /tmp/engineering-bar/twilio-credential-shapes-external/repo check`:
  passed the same full gate from an external temporary repository path.
