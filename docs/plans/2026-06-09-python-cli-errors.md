# Python CLI Errors

## Status: Completed

## Context

The Node.js sample catches top-level send errors and prints a concise message.
The Python sample called `main()` directly, so expected configuration problems
such as missing `TWILIO_TO`, `TWILIO_FROM`, or `TWILIO_BODY` produced a Python
traceback instead of a clear sample error.

## Objectives

- Keep Python sample validation errors concise for local CLI use.
- Preserve non-zero process exit behavior on expected setup failures.
- Add test coverage that expected validation errors do not print tracebacks.

## Work Completed

- Changed `main()` to catch `ValueError` and `RuntimeError`, write the message
  to stderr, and return `1`.
- Changed direct execution to `raise SystemExit(main())`.
- Added a unittest covering missing settings without traceback output.
- Updated README, VISION, and CHANGES with the new CLI guard.

## Verification

- `python3 -m unittest discover -s tests -p 'test_company_comms.py' -k test_main_reports_validation_errors_without_traceback`
- `make lint`
- `make test`
- `make build`
- `make check`
- `make verify`
- `git diff --check`

## Follow-Up Candidates

- Add mocked Twilio client examples for local live-send development.
- Add language-specific dependency manifests for easier setup.
