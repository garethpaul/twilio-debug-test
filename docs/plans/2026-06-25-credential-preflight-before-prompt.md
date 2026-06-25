# Credential Preflight Before Prompt

Status: Completed

## Problem

Python and Node.js validated the live recipient, then requested the operator's
one-shot execution confirmation before checking whether Twilio credentials were
present and structurally valid. A send that could never reach client setup could
therefore still ask the operator to authorize it.

## Design

- Preserve dry-run behavior without reading or validating credentials.
- Preserve matching `TWILIO_CONFIRM_TO` validation before credential access.
- Validate required Account SID and auth-token values before interactive or
  noninteractive execution confirmation.
- Keep client import and construction after per-invocation confirmation.
- Apply the same ordering in Python and Node.js.

## Test-First Evidence

- RED: both focused tests observed one prompt invocation for malformed Account
  SID input.
- GREEN: malformed credentials now raise the owned credential error with zero
  prompt calls and zero client-factory calls.
- Two hostile ordering mutations that move either prompt before credential
  validation were rejected by the canonical baseline.

## Verification

- Focused Python unit tests and Node.js contracts passed.
- Repository and external-directory `make check` passed.
- Python, JavaScript, shell syntax, dependency installation, package audits,
  whitespace checks, and the canonical ordering baseline passed.
- No Twilio credentials were loaded and no live message was sent.
