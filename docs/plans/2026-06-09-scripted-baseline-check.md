# Scripted Baseline Check

## Status: Completed

## Context

The repository has a useful Makefile gate for Python and Node.js sample checks,
but repository-level assumptions such as required files, completed plans, and
local editor metadata hygiene were not visible through a scriptable baseline
guard.

## Objectives

- Keep `make check` as the root verification command.
- Add a script-level baseline guard for required repository files.
- Check completed docs-plan metadata without needing to inspect Python tests.
- Ignore common local editor metadata for the mixed Python and Node.js sample.

## Work Completed

- Added `scripts/check-baseline.sh`.
- Wired the script into `make check` after the existing verification gate.
- Added `.idea/`, `.vscode/`, and `*.iml` to `.gitignore`.
- Added Python docs-plan coverage that keeps the scripted baseline guard in the
  Makefile.
- Updated README, VISION, and CHANGES.

## Verification

- `python3 -m unittest discover -s tests -p 'test_*.py'`
- `node tests/test_js_contracts.js`
- `make check`
- `git diff --check`

## Follow-Up Candidates

- Add language-specific dependency manifests if these samples need reproducible
  dependency installation.
- Expand the baseline script with dependency checks after manifests exist.
