# Live Execution Confirmation

Status: Completed

## Problem

The existing live-send flags and matching recipient value could remain in an
operator's environment. A later CLI rerun or noninteractive job would then
create a Twilio message immediately, without a per-invocation human checkpoint.
Retry behavior was also inherited from helper-library defaults rather than
being stated at the message-creation boundary.

## Decision

- Preserve credential-free dry-run behavior.
- After recipient validation, require interactive users to type `send ####`,
  using only the redacted recipient and its final four digits in the prompt.
- Fail closed when stdin is absent, unreadable, or noninteractive.
- Permit intentional automation only with the explicit
  `TWILIO_ALLOW_NONINTERACTIVE=true` environment setting.
- Perform this gate before credential access, client construction, or provider
  calls.
- Configure Python `max_retries=0` and Node `autoRetry:false` explicitly.

## Verification

- Python and Node fake-provider tests first failed because the clients were
  reached without a per-invocation gate.
- Regression tests cover noninteractive refusal, unreadable stdin, mismatched
  confirmation, redacted prompts, successful one-shot confirmation, and the
  explicit automation override.
- Provider constructor tests require explicit retry-disable options.
- `make check` validates syntax, unit and CLI behavior, package pins, audits,
  baseline contracts, and external-directory execution without live Twilio
  calls.
