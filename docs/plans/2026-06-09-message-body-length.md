# Message Body Length Guard

## Status: Completed

## Context

The Python and Node.js samples required a non-blank message body but did not
bound body length. For a debug-send sample, accepting unexpectedly large bodies
increases the chance of accidental live-send surprises and noisy logs.

## Objectives

- Keep both language samples aligned on a 1600-character message body limit.
- Reject oversized bodies before dry-run output or live Twilio client setup.
- Preserve existing trimming, redaction, and missing-setting behavior.
- Add regression coverage in Python and Node.js.

## Work Completed

- Added `MAX_MESSAGE_BODY_LENGTH = 1600` to the Python sample.
- Added `MAX_MESSAGE_BODY_LENGTH = 1600` to the Node.js sample export.
- Rejected oversized message bodies in both payload builders.
- Added Python unittest and Node.js contract coverage.
- Updated README, VISION, and CHANGES.

## Verification

- Negative: source review showed non-blank bodies were accepted with no length
  limit before dry-run or live-send setup.
- `python3 -m py_compile test.py tests/test_company_comms.py tests/test_docs_plans.py`
- `node --check test.js`
- `node --check tests/test_js_contracts.js`
- `python3 -m unittest discover -s tests -p 'test_*.py'`
- `node tests/test_js_contracts.js`
- `make check`
- `make verify`
- `git diff --check`

## Follow-Up Candidates

- Document how Twilio segments longer SMS bodies if the sample grows beyond
  simple debug sends.
- Add language-specific dependency manifests for easier fresh setup.
