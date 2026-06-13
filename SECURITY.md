# Security Policy

## Supported Versions

The supported security scope for `twilio-debug-test` is the current default branch, `main`. Older commits, tags, branches, forks, demos, and generated artifacts are not actively supported unless the repository explicitly marks them as maintained.

Project summary: Debug Demo

## Reporting a Vulnerability

Please report suspected vulnerabilities through GitHub's private vulnerability reporting or by opening a draft GitHub Security Advisory for `garethpaul/twilio-debug-test` when that option is available. If GitHub does not show a private reporting option for this repository, contact the repository owner through GitHub and avoid posting exploit details publicly until the issue can be assessed.

Do not open a public issue that includes exploit code, secrets, personal data, or detailed reproduction steps for an unpatched vulnerability.

## What to Include

Helpful reports include:

- the affected file, endpoint, permission, dependency, or workflow
- a concise impact statement explaining what an attacker could do
- reproduction steps using test data and accounts you control
- the branch, commit SHA, platform version, device, runtime, or dependency versions used
- logs, screenshots, or proof-of-concept snippets that demonstrate impact without exposing private data

## Project Security Posture

- This repository appears to be a public sample, documentation, or utility project. The active security scope is the code and documentation on the default branch.
- Review found authentication, token, or session-related code paths; changes in those areas should receive security-focused review before merge.
- Review found external API integrations or credential-adjacent configuration; changes in those areas should receive security-focused review before merge.
- Review found network clients, sockets, web APIs, or service endpoints; changes in those areas should receive security-focused review before merge.
- Review found file, document, data, or media parsing flows; changes in those areas should receive security-focused review before merge.
- No primary dependency manifest was detected in the repository root. If dependencies are added later, include a manifest and prefer reproducible installation instructions.
- GitHub Actions uses immutable action pins, read-only repository permissions,
  credential-free checkout, a fixed Ubuntu 24.04 runner, and a bounded runtime
  while exercising the Python and Node.js sample checks on every push and pull
  request.
- Command-line output must redact Twilio resource identifiers and must not emit
  unexpected provider error details that may contain credentials, phone
  numbers, request URLs, or message metadata.
- Python and Node.js expose local validation details only for sample-owned error
  types; provider-controlled message prefixes are never trusted.
- Explicit blank Python message arguments must fail validation instead of
  falling back to an environment recipient, sender, or body.
- Python and Node.js sender and recipient settings must pass the shared E.164
  shape check before dry-run output or live Twilio client construction.
- Live mode must require a separate E.164 `TWILIO_CONFIRM_TO` value that matches
  the normalized `TWILIO_TO` recipient before credential or client setup.
- Live mode requires the canonical Account SID and auth-token ASCII hexadecimal
  shapes before client construction. This rejects malformed local
  configuration but does not establish credential validity or authorization.

## Service and API Notes

For web services, APIs, sockets, or scraping workflows, prioritize reports involving authentication bypass, authorization errors, injection, server-side request forgery, unsafe deserialization, credential leakage, data exposure, or denial-of-service conditions. Use test accounts and minimal proof-of-concept traffic only.

## Dependency and Supply Chain Security

Dependency updates should come from trusted package managers and should keep lockfiles in sync when lockfiles exist. Do not commit credentials, private keys, tokens, generated secrets, or machine-local configuration. If a vulnerability depends on a compromised package, typosquatting risk, insecure transitive dependency, or unsafe build step, include the package name, affected version, and the path through which it is used.

The Python sample pins its direct Twilio runtime dependency and the pip/pip-audit
tool inputs. `make check` installs them in an isolated temporary environment,
checks the resolved dependency set, and audits the runtime manifest without
using Twilio credentials or making a live API request.

## Safe Research Guidelines

Good-faith research is welcome when it stays within these boundaries:

- use only accounts, devices, data, and infrastructure that you own or have explicit permission to test
- avoid destructive actions, persistence, spam, phishing, social engineering, or denial-of-service testing
- minimize access to personal data and stop testing immediately if private data is exposed
- do not exfiltrate secrets or third-party data; report the minimum evidence needed to verify impact
- keep vulnerability details confidential until the maintainer has assessed the report

## Maintainer Response

The maintainer will review complete reports as availability allows, prioritize issues by exploitability and impact, and coordinate a fix or mitigation when the affected code is still maintained. For sample, archived, or educational repositories, the likely remediation may be documentation, dependency updates, or clearly marking unsupported code rather than a production-style patch release.
