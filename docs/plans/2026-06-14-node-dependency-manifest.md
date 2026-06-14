# Node Dependency Manifest

## Status: Completed

## Context

The Node sample imports Twilio only on an explicitly confirmed live-send path,
but the repository has no Node manifest or lockfile. A contributor cannot
reproduce or audit the helper-library version that live mode would load.

## Priority

Pin the current stable Twilio Node helper behind a private package manifest,
commit its lockfile, and make installation and vulnerability auditing part of
the canonical path-independent gate.

## Requirements

- Add a private package manifest with exact `twilio@6.0.2` and Node 20 or newer.
- Commit a package-lock generated without lifecycle scripts.
- Install the lockfile with `npm ci --ignore-scripts` before auditing runtime
  dependencies.
- Preserve dry-run defaults, injected fake clients, credential validation,
  recipient confirmation, redaction, and Python package verification.
- Keep `NPM` configurable while protecting the repository-root path.
- Add fail-closed manifest, lockfile, Make, documentation, suite, and plan
  contracts plus hostile mutations.

## Verification

- Focused Node contracts and package metadata checks passed.
- The repository and external-directory `make check` passed.
- `npm ci --ignore-scripts` and the production `npm audit` passed with zero
  known vulnerabilities.
- Nine hostile Node package mutations were rejected across the package version,
  lockfile, engine, privacy, install, audit, documentation, suite, and plan
  status contracts.
- Final artifact, credential, exact-diff, and hosted matrix audits remain the
  shipping gate.

## Scope Boundary

This change does not perform a live Twilio send, add credentials, bundle
`node_modules`, change the Python dependency version, or alter sample output.
