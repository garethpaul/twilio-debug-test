# Make Authority Hardening

## Status: Completed

## Context

The portable `make check` gate protected its root but still accepted Make-syntax
tool values, caller shells, execution-skipping flags, startup files, and Makefile
identity replacement.

## Requirements

- Preserve literal Python, Node.js, and npm executable overrides.
- Provide a fixed-target entrypoint before GNU Make parses caller-controlled
  startup files, options, evaluations, or additional makefiles.
- Reject Make-syntax tools before expansion and keep root/shell authority local.
- Prove repository and external-directory `make check` behavior.
- Keep all Twilio credentials unset and all live provider calls disabled.

## Work Completed

- Bound root, shell, tool, flag, startup-file, and Makefile identity authority.
- Added `scripts/run-make.sh` with exact `check|lint` targets, five-variable Make
  environment sanitization, fixed tools, and byte-preserving physical symlink
  resolution; both hosted verification steps use this entrypoint.
- Added executable adversarial regression coverage to `make check`.
- Reproduced raw `-n`/`-i` plus `--eval`, `GNUMAKEFLAGS`, executable
  `MAKEFILES`, and earlier/later `-f` authority before proving wrapper exclusion.

## Verification

- Sanitized repository and external-directory `make check` passed using public
  PyPI and npm registries with live sending disabled.
- No Twilio credentials, provider endpoints, recipients, or live sends were used.

## Scope Boundaries

No sample behavior, dependency version, credential handling, provider request,
publishing, or deployment changed. Literal `PYTHON`, `NODE`, and `NPM` paths
remain caller authority. Direct GNU Make startup files, options, evaluations,
and earlier or later caller-supplied `-f` files remain outside the wrapper.
