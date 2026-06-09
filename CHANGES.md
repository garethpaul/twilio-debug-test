# Changes

## 2026-06-09

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
