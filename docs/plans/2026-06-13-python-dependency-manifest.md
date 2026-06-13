# Python Dependency Manifest

## Status: Completed

## Context

The Python sample lazily imports the Twilio helper library only for live sends,
while tests inject a fake client. That keeps local validation credential-free
but leaves the actual runtime dependency and audit toolchain undeclared and
unverified by the canonical repository gate.

## Priority

Pin the Python runtime dependency and package-audit tools, then make `make
check` prove that an isolated environment can install, import, validate, and
audit the reviewed package set across the hosted Python matrix.

## Requirements

- R1. Pin the Twilio Python helper library to the reviewed official PyPI
  release.
- R2. Pin pip and pip-audit versions used by the package gate.
- R3. Install the declared files in an isolated temporary virtual environment
  without inheriting `PYTHONPATH`.
- R4. Verify the installed Twilio version and import, then run `pip check` and
  audit the runtime manifest for known vulnerabilities.
- R5. Include the package gate in canonical `make check` and preserve external
  working-directory execution.
- R6. Keep Python 3.10, 3.12, and 3.14 hosted coverage and all Node.js checks.
- R7. Add fail-closed source, workflow, documentation, plan, and hostile
  mutation contracts without credentials or live API calls.

## Implementation Units

### Declare and verify Python packages

**Files:** `requirements.txt`, `requirements-dev.txt`,
`scripts/check-python-package.sh`, `Makefile`

Pin the runtime and audit inputs. Build a disposable virtual environment,
install only from the reviewed manifests, assert the Twilio distribution
version and import, check dependency consistency, and audit runtime packages.

### Preserve contracts and maintenance records

**Files:** `scripts/check-baseline.sh`, `tests/test_docs_plans.py`, `README.md`,
`SECURITY.md`, `VISION.md`, `CHANGES.md`,
`docs/plans/2026-06-13-python-dependency-manifest.md`

Require the manifests, exact package pins, isolated gate, Make integration,
hosted matrix, documentation, and completed verification record.

## Verification Plan

- focused Python and Node test suites
- full canonical `make check` and external-working-directory gate under hard
  timeouts
- package version/import, `pip check`, and runtime `pip-audit`
- hostile mutations for either pin, environment isolation, import/version
  assertion, dependency check, audit, Make integration, documentation, and plan
  status
- shell syntax, Python compilation, workflow parsing, intended-path,
  generated-artifact, whitespace, and changed-line secret audits

## Scope Boundaries

- Do not add a Node package manifest in this change.
- Do not change send behavior, credentials, recipient confirmation, logging,
  message validation, runtime matrix versions, or make a live Twilio request.
- Do not claim a fully hash-locked transitive dependency graph; this change
  pins the direct runtime and audit tool inputs and verifies their resolved
  environment.

## Work Completed

- Pinned `twilio==9.10.9`, `pip==26.1.2`, and `pip-audit==2.10.0` in separate
  runtime and audit manifests.
- Added an isolated temporary-venv gate that removes `PYTHONPATH`, installs the
  manifests, verifies the Twilio distribution version and import, checks the
  resolved environment, and audits the runtime manifest.
- Integrated the package gate into canonical `make check` while preserving the
  existing Python/Node behavior suites, hosted matrix, and external-directory
  validation.
- Extended shell and Python contracts plus security, maintenance, and roadmap
  documentation for the pinned package boundary.

## Verification

- The focused Python suite passed 26 tests with `PYTHONPATH` removed, and the
  Node.js contract suite passed without live Twilio requests.
- The isolated Python 3.12.12 package gate completed under a 240-second hard
  timeout: `twilio==9.10.9` installed and imported, `pip check` reported no
  broken requirements, and `pip-audit` reported no known vulnerabilities.
- Full repository and external-working-directory `make check` passed under
  explicit hard timeouts, including the package gate and all existing behavior
  and baseline contracts.
- Focused hostile mutations for package pins, environment isolation,
  version/import verification, dependency checking, auditing, Make integration,
  documentation, and completed plan status were rejected.
- Shell syntax, Python compilation, workflow parsing, intended-path,
  generated-artifact, `git diff --check`, and changed-line secret audits passed
  before shipment.
