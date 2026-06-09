# Node Credential Errors

## Status: Completed

## Context

The Python sample reports both missing Twilio credential names before live-send
setup. The Node.js sample validated credential settings one at a time, which
made CLI feedback less complete and increased the chance of reaching package
loading or client setup before the full configuration problem was visible.

## Objectives

- Validate Node.js live-send credentials before requiring or constructing a
  Twilio client.
- Report all missing credential names in one concise CLI error.
- Keep dry-run message setting validation behavior unchanged.
- Add no-network Node.js coverage through the exported CLI runner.
- Keep the completed plan required by `make check`.

## Work Completed

- Added `missingSettings` for grouped Node.js setting validation.
- Changed live-send credential validation to report missing SID and token
  together.
- Added Node.js CLI coverage for combined missing-credential errors.
- Updated docs-plan tests to require this completed plan.
- Updated README, VISION, and CHANGES.

## Verification

- `node --check test.js`
- `node --check tests/test_js_contracts.js`
- `node tests/test_js_contracts.js`
- `python3 -m unittest discover -s tests -p 'test_*.py'`
- `make check`
- `git diff --check`

## Follow-Up Candidates

- Add language-specific dependency manifests.
- Add deeper examples for redacting shared debug logs.
