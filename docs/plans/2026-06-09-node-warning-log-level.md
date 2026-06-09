# Node Warning Log Level

## Status: Completed

## Context

The Python sample accepts both `warn` and `warning` as warning-level log input,
but the Node.js sample only accepted `warn`. That made a reasonable
`TWILIO_LOG_LEVEL=warning` value silently fall back to `info`, even though it is
still a safe, non-debug logging level.

## Objectives

- Keep Node.js live-send logging at `info` by default.
- Preserve explicit opt-in for supported log levels.
- Normalize `warning` to Twilio's `warn` log level.
- Cover the alias with the existing Node.js contract test.

## Work Completed

- Replaced the Node.js log-level allow-list with an alias map.
- Added `warning -> warn` normalization.
- Added a Node.js contract assertion for the alias.
- Updated README, VISION, and CHANGES.

## Verification

- `node --check test.js`
- `node tests/test_js_contracts.js`
- `make check`
- `make verify`
- `git diff --check`

## Follow-Up Candidates

- Add mocked Twilio client examples for local live-send development.
- Add language-specific dependency manifests for easier setup.
