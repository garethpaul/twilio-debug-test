# Make Root Protection

## Status: Planned

## Context

The Makefile currently sets `ROOT` from `CURDIR`. Invoking it with `-f` from an
external working directory therefore redirects source, test, package, and
baseline paths even without an explicit override. Environment and command-line
`ROOT` assignments can redirect them again through GNU Make precedence.

Python and Node selection are intentionally configurable. Repository ownership
is not: every command must remain anchored to the checkout containing the
invoked Makefile.

## Requirements

- Derive the repository root from the Makefile path rather than the caller's
  working directory.
- Protect that derived root from environment and command-line reassignment.
- Preserve explicit `PYTHON` and `NODE` overrides and all six public aliases.
- Prove repository and external working-directory invocations remain anchored
  under ordinary and hostile root conditions.
- Add mutation-sensitive contracts for declaration shape/count/order, aliases,
  source/test/package/baseline paths, README index, and completed plan.
- Preserve Twilio credential, confirmation, CLI privacy, dependency, workflow,
  and runtime behavior.

## Approach

Replace the current-directory assignment with one protected immediate
assignment derived from the last loaded Makefile. Keep it before configurable
Python and Node declarations. Extend the existing shell baseline checker and
use bounded dry-run and mutation cases before the full pinned package gate.

## Implementation Units

### Anchor and protect the repository root

- Update `Makefile` with exactly one protected Makefile-derived root.
- Retain the current alias graph and tool overrides.

### Add adversarial contracts

- Extend `scripts/check-baseline.sh` with exact declaration, assignment-count,
  ordering, alias, path, README, and plan requirements.
- Run all six aliases from repository and external directories with ordinary,
  environment, and command-line root conditions.
- Reject declaration, duplication, ordering, alias, path, documentation, and
  plan-state mutations.

### Record completed evidence

- Index this plan from `README.md`.
- Mark it completed only after focused, mutation, full package, review,
  artifact, secret, and exact-diff validation succeeds.

## Risks And Mitigations

- Protecting tool variables would break supported runtime-matrix selection.
  Only `ROOT` becomes protected; `PYTHON ?=` and `NODE ?=` remain unchanged and
  receive explicit override checks.
- String-only validation could miss another root assignment or alias bypass.
  Count all assignments and require every repository-owned command path.
- Package validation must remain offline from Twilio. Use fake-client tests and
  the existing pinned dependency audit without live credentials or requests.

## Scope Boundaries

This change does not modify Python or JavaScript message behavior, credential
validation, recipient confirmation, logging, CLI redaction, dependency pins,
workflow policy, or deployment behavior.

## Verification Plan

- Run focused baseline and Make dry-run checks.
- Exercise all aliases from repository and external directories under ordinary
  and hostile root assignments while preserving Python and Node selection.
- Reject eight focused structural and evidence mutations.
- Run the full pinned `make check` gate with an explicit timeout.
- Review the exact plan-scoped diff and audit generated artifacts, changed-line
  secrets, whitespace, and protected application/test/workflow/dependency paths.
