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

Next priorities:

- Add a dry-run mode or mocked send examples
- Replace hardcoded phone-number arguments with environment-only values
- Add setup notes for each language sample
- Document how to redact logs before sharing them

Contribution rules:

- One PR = one focused language example, logging, send flow, or documentation change.
- Do not commit credentials, phone numbers, message SIDs, or customer data.
- Keep live-send examples clearly labeled.
- Add redaction guidance for debug output.

## Security And Responsible Use

Debug logs can expose account credentials, phone numbers, URLs, and message
content. Examples should favor redaction, environment variables, and mock paths
before live sends.

## What We Will Not Merge (For Now)

- Checked-in credentials or phone numbers
- Logs containing auth headers or customer payloads
- Live-send defaults without clear opt-in
- Debug settings that persist beyond the sample

This list is a roadmap guardrail, not a permanent rule.
Strong user demand and strong technical rationale can change it.
