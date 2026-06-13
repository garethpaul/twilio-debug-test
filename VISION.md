## Twilio Debug Test Vision

Twilio Debug Test is a small collection of examples showing how to enable
debug logging in Twilio helper libraries and send test messages from Node.js
and Python.

The repository is useful as a troubleshooting reference for local debugging
patterns across languages, with concrete environment-variable based examples.

The goal is to keep debugging examples practical while preventing accidental
credential, phone-number, or message-body exposure.

The current focus is:

Priority:

- Preserve language-specific debug logging snippets
- Keep Twilio credentials in environment variables
- Avoid logging secrets, auth headers, or full customer payloads
- Treat live message sending as an explicit opt-in action
- Keep default sample execution in dry-run mode
- Normalize required settings before validation and redaction
- Keep explicit Python message arguments authoritative, including invalid blanks
- Validate sender and recipient settings consistently as E.164 values
- Require a separate matching recipient confirmation before any live-send
  credential or client setup
- Bound sample message bodies before dry-run output or live send setup
- Report expected sample setup errors without tracebacks
- Keep CLI validation errors testable across language samples
- Keep a scriptable baseline guard for required files and maintenance metadata
- Report missing Node.js message settings together before sample send setup
- Report missing Twilio live-send credentials together before client setup
- Reject malformed Account SID and auth-token shapes before client setup
- Keep live-send debug logging as an explicit opt-in across language samples
- Keep language log-level aliases normalized before applying Twilio settings
- Keep live-send paths testable with mocked clients
- Keep live-send Message SIDs redacted in command-line output
- Keep unexpected provider diagnostics out of user-facing stderr
- Allowlist sample-owned Python validation exceptions instead of broad built-in types
- Allowlist sample-owned Node.js validation exceptions instead of message prefixes
- Keep the Python and Node.js compatibility matrix enforced in hosted CI
- Keep hosted checks unfiltered across branches and independent of caller paths

Next priorities:

- Add language-specific dependency manifests
- Add setup notes for each language sample
- Add deeper redaction examples for shared debug logs

Contribution rules:

- One PR = one focused language example, logging, send flow, or documentation change.
- Do not commit credentials, phone numbers, message SIDs, or customer data.
- Keep live-send examples clearly labeled.
- Add redaction guidance for debug output.

## Security And Responsible Use

Canonical security policy and reporting:

- [`SECURITY.md`](SECURITY.md)

Debug logs can expose account credentials, phone numbers, URLs, and message
content. Examples should favor redaction, environment variables, and mock paths
before live sends.

## What We Will Not Merge (For Now)

- Checked-in credentials or phone numbers
- Logs containing auth headers or customer payloads
- Live-send defaults without clear opt-in
- Unbounded message bodies in debug-send samples
- Debug settings that persist beyond the sample
- Language-specific log-level aliases that silently fall back to another level

This list is a roadmap guardrail, not a permanent rule.
Strong user demand and strong technical rationale can change it.
