# Align dry-run body length reporting

## Status: Completed

## Problem

Python validation counted UTF-16 code units, but its privacy-safe dry-run
`body_length` metadata still used `len()` and reported Unicode code points.
Eight hundred emoji therefore passed at the 1600-unit limit while Python
reported 800 and Node.js reported 1600 for the same body.

## Fix

- Route Python dry-run metadata through `message_body_units`.
- Route Node.js dry-run metadata through `messageBodyUnits` instead of relying
  on the equivalent native `.length` behavior implicitly.
- Describe oversized bodies as UTF-16 code units in both validation errors.
- Keep message contents private and preserve the existing metadata field names.

## Test First

The focused Python regression failed with `800 != 1600`. A Node.js source
contract also failed until its dry-run path used the shared helper explicitly.

## Verification

- Run the focused Python Unicode-body test and Node.js contract suite.
- Run repository and external-directory `make check`.
- Run isolated mutations replacing each helper call with the former raw length.
- Run syntax, whitespace, and package audit gates.
