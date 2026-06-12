# CI Baseline

Status: Completed

## Context

The repository had local Python and Node `make check` verification for the
Twilio debug samples, but no hosted workflow ran it for pushes and pull
requests.

## Changes

- Added a GitHub Actions workflow that installs Python 3.12 and Node 20, then
  runs `make check`.
- Extended the baseline guard and docs so the hosted CI path stays visible.

## Verification

- `make check`
