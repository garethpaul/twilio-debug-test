# Changes

## 2026-06-14

- Added pinned, least-privilege CodeQL analysis for GitHub Actions, Python, and
  JavaScript/TypeScript to every hosted push and pull request.
- Added a private Node manifest and lockfile for exact `twilio@6.0.2`, plus
  script-disabled installation, structured package contracts, and production
  vulnerability auditing in `make check`.

## 2026-06-13

- Added pinned Python Twilio, pip, and pip-audit manifests plus an isolated
  install, import, dependency-consistency, and vulnerability gate.
- Required a separate E.164 `TWILIO_CONFIRM_TO` value matching the normalized
  recipient before live-send credential or client setup in both runtimes.
- Added fail-closed ordering, dry-run independence, normalization, and safe CLI
  coverage for the live-recipient confirmation boundary.
- Required live-mode Account SIDs and auth tokens to match their canonical
  ASCII hexadecimal shapes before either Twilio client factory runs.
- Added cross-runtime boundary, ordering, dry-run, and CLI privacy coverage for
  malformed credential configuration.

## 2026-06-12

- Required Python and Node.js sender and recipient settings to use a trimmed
  E.164 shape before dry-run output or live client construction.
- Added shared boundary, malformed-input, and concise CLI-error coverage for
  both runtimes.
- Stopped explicit blank Python message arguments from silently falling back
  to environment recipients, senders, or bodies.
- Added fail-closed override tests that verify invalid explicit values are
  rejected before Twilio client construction.
- Avoided reading environment fallbacks when all Python message arguments are
  explicitly supplied.
- Made external verification safe for repository paths containing spaces and
  allowed Node.js CLI output to flush before process termination.

## 2026-06-10

- Allowlisted sample-owned Python validation exceptions so provider-raised
  built-in `RuntimeError` and `ValueError` details remain redacted.
- Allowlisted sample-owned Node.js validation exceptions so provider-controlled
  messages cannot impersonate local configuration errors and bypass redaction.
- Redacted Twilio Message SIDs in Python and Node.js command-line success output
  while preserving full SDK results for programmatic callers.
- Added generic handling for unexpected provider errors so CLI stderr cannot
  expose fake or real credentials, phone numbers, URLs, or message metadata.
- Extended both runtime test suites with provider-failure and identifier-
  redaction coverage.
- Fixed CI to Ubuntu 24.04, upgraded action annotations and setup-node to
  v6.4.0, scoped concurrency, and made Make targets root-independent.
- Added a pinned, read-only GitHub Actions matrix covering Python 3.10, 3.12,
  and 3.14 with Node.js 20, 22, and 24 on every push and pull request.
- Disabled checkout credential persistence and added an external-working-
  directory run of the full gate to each hosted matrix job.
- Extended the local baseline and docs-plan tests to protect the hosted CI
  contract.

## 2026-06-09

- Added a shared 1600-character message body limit to Python and Node.js sample
  payload validation.
- Reported all missing Node.js message setting names together for dry-run and
  live-send setup validation.
- Added `scripts/check-baseline.sh` to keep required files, completed plan
  metadata, verification docs, and editor metadata hygiene wired into
  `make check`.
- Added Node.js CLI coverage for combined missing message-setting errors.
- Reported all missing Node.js live-send credential names before importing or
  constructing a Twilio client.
- Added Node.js CLI coverage for combined missing-credential errors.
- Added a testable Node.js CLI runner that returns exit codes and reports
  expected validation errors without stack traces.
- Added an injectable Node.js Twilio client factory for mocked live-send tests.
- Added Node.js fake-client coverage for live-send payloads and default log
  level assignment.
- Made the Python sample entry point return a non-zero exit code with a concise
  stderr validation message instead of a traceback for expected setup errors.
- Added Python test coverage for traceback-free CLI validation failures.
- Normalized Node.js `TWILIO_LOG_LEVEL=warning` to Twilio's `warn` log level.
- Added a Node.js contract assertion for the warning alias.

## 2026-06-08

- Added Python live-send log-level opt-in handling and fake-client tests.
- Changed the Node.js live-send log level default from `debug` to `info`, while
  preserving explicit `TWILIO_LOG_LEVEL=debug` opt-in coverage.
- Added canonical `docs/plans` coverage to the Python test suite.
- Normalized Twilio sample environment settings before validation so
  whitespace-padded values do not leak into dry-run output or live-send setup.
- Added Python and Node.js tests for trimmed settings, blank message bodies,
  and whitespace-tolerant live-send opt-in flags.
- Added `make check` as the shared repository verification alias.
- Added Python and Node.js tests plus a `make verify` gate.
- Changed both Twilio samples to dry-run by default and require `TWILIO_SEND_LIVE=true` for live sends.
- Removed hardcoded phone numbers and message bodies from executable sample paths.
