# Node CLI Runner

## Status: Completed

## Context

The Node.js sample caught top-level errors when executed directly, but that
behavior lived inside the `require.main` block. The Python sample has a
testable `main()` return code path, and the Node sample should offer the same
kind of no-network coverage for expected configuration failures.

## Objectives

- Preserve direct `node test.js` behavior.
- Expose a testable Node.js CLI runner that returns an exit code.
- Keep expected validation errors concise and stack-trace free.
- Cover the runner without importing Twilio or sending messages.

## Work Completed

- Added `runCli(env, logError)` to wrap `sendMessage()`.
- Changed direct execution to call `runCli()` and exit with its return code.
- Exported `runCli` for tests.
- Extended `tests/test_js_contracts.js` to cover missing configuration errors.
- Updated README, VISION, and CHANGES.

## Verification

- Negative check before implementation:
  `node tests/test_js_contracts.js` failed because `sample.runCli` was not
  exported.
- `node --check test.js`
- `node --check tests/test_js_contracts.js`
- `node tests/test_js_contracts.js`
- `python3 -m unittest discover -s tests -p 'test_*.py'`
- `make check`
- `make verify`
- `git diff --check`
