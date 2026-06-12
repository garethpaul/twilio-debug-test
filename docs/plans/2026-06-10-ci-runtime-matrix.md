# CI Runtime Matrix

## Status: Completed

## Context

The repository had a thorough local `make check` gate but no hosted workflow.
That left Python and Node.js compatibility dependent on a maintainer running the
checks locally, and gave pull requests no automatic regression signal.

## Objectives

- Run the existing repository gate for pushes, pull requests, and manual runs.
- Cover representative maintained Python and Node.js release combinations.
- Pin third-party actions to immutable commit SHAs.
- Keep workflow permissions read-only and bound execution time.
- Make the local baseline reject accidental weakening of the workflow contract.

## Work Completed

- Added a three-entry Python 3.10/3.12/3.14 and Node.js 20/22/24 matrix.
- Pinned checkout, Python setup, and Node.js setup actions to commit SHAs.
- Set explicit read-only contents permission and a ten-minute job timeout.
- Extended the baseline script and docs-plan test to require the hosted gate.
- Documented the compatibility baseline in project maintenance guidance.

## Verification

- `make check`
- `make verify`
- `git diff --check`
- Reviewed the workflow for pinned actions, least-privilege permissions, and a
  bounded timeout.

## Follow-Up Candidates

- Add dependency manifests if the samples begin importing Twilio during local
  dry-run checks.
- Revisit the oldest matrix entries as upstream language support changes.
