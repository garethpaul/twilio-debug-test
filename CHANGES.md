# Changes

## 2026-06-08

- Normalized Twilio sample environment settings before validation so
  whitespace-padded values do not leak into dry-run output or live-send setup.
- Added Python and Node.js tests for trimmed settings, blank message bodies,
  and whitespace-tolerant live-send opt-in flags.
- Added `make check` as the shared repository verification alias.
- Added Python and Node.js tests plus a `make verify` gate.
- Changed both Twilio samples to dry-run by default and require `TWILIO_SEND_LIVE=true` for live sends.
- Removed hardcoded phone numbers and message bodies from executable sample paths.
