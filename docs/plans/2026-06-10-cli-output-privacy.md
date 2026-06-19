# CLI Output Privacy

## Status: Completed

## Context

The samples correctly redacted phone numbers during dry runs, but live-send
success output printed the complete Twilio Message SID. The CLIs also emitted
unexpected provider exception messages verbatim, which can contain request
URLs, phone numbers, message metadata, or credential-adjacent diagnostics.

## Objectives

- Preserve full Twilio result objects for programmatic callers.
- Redact Message SIDs before printing live-send success output.
- Preserve actionable local validation errors.
- Replace unrecognized provider failures with a stable generic CLI message.
- Test both behaviors without importing Twilio or sending network requests.
- Keep the runtime matrix reproducible on a fixed runner with current immutable
  action revisions.

## Work Completed

- Added shared identifier redaction to Python and Node.js success output.
- Added safe CLI error formatting in both runtimes.
- Allowlisted Node.js validation output by sample-owned error type so provider
  exceptions cannot mimic trusted local message prefixes.
- Passed the Node.js client-factory seam through `runCli` for provider-failure
  tests.
- Added Python and Node.js tests proving fake secret-bearing diagnostics are not
  printed and successful SIDs are redacted.
- Fixed CI to Ubuntu 24.04, setup-node 6.4.0, annotated action pins, scoped
  concurrency, and root-independent Make commands.

## Verification

- `make check`
- `make -C "/path/to/twilio debug test" check` outside the repository
- Python 3.10/3.12/3.14 and Node.js 20/22/24 hosted matrix
- SID-redaction, provider-error, runner, action, and Makefile mutations rejected
- `git diff --check`
