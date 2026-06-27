# Unicode Message Body Units

## Status: Completed

## Context

Twilio limits message bodies to 1600 characters and documents that emoji and
other special characters can consume multiple units. JavaScript string length
already counts UTF-16 code units, while Python `len()` counts Unicode code
points. The samples therefore disagreed, and Python could admit an emoji-heavy
body that Node.js and the provider would reject.

## Decision

- Define the cross-runtime boundary as 1600 UTF-16 code units.
- Count Python text by encoding with UTF-16 little endian and dividing bytes by
  two, using surrogate-pass behavior to match JavaScript string semantics.
- Route Node.js validation through an explicit helper even though native string
  length already has the required semantics.
- The initial rollout kept Python dry-run `body_length` as a code-point count.
  That reporting choice is superseded by
  `2026-06-27-dry-run-body-unit-reporting.md`; both runtimes now report the same
  UTF-16 units they validate.

## Verification

- Python and Node.js accept 800 emoji (1600 UTF-16 units).
- Python and Node.js reject 801 emoji (1602 UTF-16 units).
- Focused suites and canonical `make check` cover the boundary.
- Repository and external-directory `make check` must pass before merge.
