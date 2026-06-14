# CodeQL Analysis

## Status: Completed

## Context

The hosted runtime matrix verifies both samples and their dependency audits,
but GitHub reports no code-scanning analysis for the repository. Source and
workflow changes therefore lack a first-party static security signal.

## Priority

Add pinned, least-privilege CodeQL analysis to the existing hosted workflow
without weakening the runtime matrix or creating a second workflow surface.

## Requirements

- Analyze GitHub Actions, Python, and JavaScript/TypeScript on every push,
  pull request, and manual workflow dispatch.
- Keep the global workflow permission read-only and grant
  `security-events: write` only to the CodeQL job.
- Pin CodeQL initialization and analysis to an immutable action SHA.
- Use the interpreted-language `none` build mode and a bounded hosted timeout.
- Preserve credential-free checkout, the complete runtime matrix, and the
  repository plus external-directory `make check` executions.
- Add fail-closed workflow and documentation contracts plus hostile mutations
  for the language matrix, permissions, pinned action, and analysis step.

## Verification

- Shell syntax, workflow YAML parsing, focused baseline contracts, and
  documentation contracts passed.
- The repository and external-directory `make check` passed.
- Four hostile CodeQL workflow mutations were rejected across the language
  matrix, upload permission, immutable action pin, and analysis step.
- Final artifact, credential, exact-diff, and hosted checks remain the shipping
  gate.

## Scope Boundary

This change does not alter sample runtime behavior, perform a live Twilio send,
add credentials, enable repository-level secret scanning, or change dependency
versions.
