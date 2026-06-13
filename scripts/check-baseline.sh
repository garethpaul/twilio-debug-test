#!/usr/bin/env sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
README="$ROOT_DIR/README.md"
MAKEFILE="$ROOT_DIR/Makefile"
GITIGNORE="$ROOT_DIR/.gitignore"
DOCS_PLANS="$ROOT_DIR/docs/plans"

require_file() {
  path=$1
  if [ ! -f "$ROOT_DIR/$path" ]; then
    printf '%s\n' "Required file is missing: $path" >&2
    exit 1
  fi
}

for path in \
  ".gitignore" \
  ".github/workflows/check.yml" \
  "CHANGES.md" \
  "Makefile" \
  "README.md" \
  "requirements.txt" \
  "requirements-dev.txt" \
  "SECURITY.md" \
  "VISION.md" \
  "test.js" \
  "test.py" \
  "tests/test_company_comms.py" \
  "tests/test_docs_plans.py" \
  "tests/test_js_contracts.js" \
  "docs/plans/2026-06-08-twilio-debug-test-baseline.md" \
  "docs/plans/2026-06-09-scripted-baseline-check.md" \
  "docs/plans/2026-06-10-ci-baseline.md" \
  "docs/plans/2026-06-10-ci-runtime-matrix.md" \
  "docs/plans/2026-06-10-cli-output-privacy.md" \
  "docs/plans/2026-06-10-python-cli-error-allowlist.md" \
  "docs/plans/2026-06-12-e164-phone-validation.md" \
  "docs/plans/2026-06-13-twilio-credential-shapes.md" \
  "docs/plans/2026-06-13-live-recipient-confirmation.md" \
  "docs/plans/2026-06-13-python-dependency-manifest.md" \
  "scripts/check-python-package.sh" \
  "scripts/check-baseline.sh"; do
  require_file "$path"
done

for credential_contract in \
  'ACCOUNT_SID_PATTERN = re.compile(r"^AC[0-9A-Fa-f]{32}$")' \
  'AUTH_TOKEN_PATTERN = re.compile(r"^[0-9A-Fa-f]{32}$")' \
  'const ACCOUNT_SID_PATTERN = /^AC[0-9A-Fa-f]{32}$/;' \
  'const AUTH_TOKEN_PATTERN = /^[0-9A-Fa-f]{32}$/;' \
  'validate_credentials(account_sid, auth_token)' \
  'validateCredentials(accountSid, authToken)' \
  'test_live_send_rejects_malformed_credentials_before_client_setup' \
  'malformed credentials must reject'; do
  if ! grep -Fq -- "$credential_contract" "$ROOT_DIR/test.py" && \
     ! grep -Fq -- "$credential_contract" "$ROOT_DIR/test.js" && \
     ! grep -Fq -- "$credential_contract" "$ROOT_DIR/tests/test_company_comms.py" && \
     ! grep -Fq -- "$credential_contract" "$ROOT_DIR/tests/test_js_contracts.js"; then
    printf '%s\n' "Twilio credential shape contract is missing: $credential_contract" >&2
    exit 1
  fi
done

python3 - "$ROOT_DIR" <<'PY'
from pathlib import Path
import sys

root = Path(sys.argv[1])
ordering_contracts = (
    ("test.py", "validate_credentials(account_sid, auth_token)", "client_factory = self.client_factory"),
    ("test.js", "validateCredentials(accountSid, authToken);", "const createClient = clientFactory"),
)
for relative_path, validation, client_setup in ordering_contracts:
    source = (root / relative_path).read_text(encoding="utf-8")
    if source.index(validation) >= source.index(client_setup):
        raise SystemExit(
            "{} must validate credential shapes before client setup.".format(relative_path)
        )
PY

for confirmation_contract in \
  'validate_live_recipient(self.env, payload["to"])' \
  'confirmation = setting_value(env.get("TWILIO_CONFIRM_TO"))' \
  'validate_phone(confirmation, "TWILIO_CONFIRM_TO")' \
  'validateLiveRecipient(env, payload.to);' \
  'const confirmation = settingValue(env.TWILIO_CONFIRM_TO);' \
  "validatePhone(confirmation, 'TWILIO_CONFIRM_TO')" \
  'TWILIO_CONFIRM_TO must match TWILIO_TO.' \
  'test_live_send_requires_matching_recipient_confirmation_before_client_setup' \
  'invalid live recipient confirmation must reject'; do
  if ! grep -Fq -- "$confirmation_contract" "$ROOT_DIR/test.py" && \
     ! grep -Fq -- "$confirmation_contract" "$ROOT_DIR/test.js" && \
     ! grep -Fq -- "$confirmation_contract" "$ROOT_DIR/tests/test_company_comms.py" && \
     ! grep -Fq -- "$confirmation_contract" "$ROOT_DIR/tests/test_js_contracts.js"; then
    printf '%s\n' "Live recipient confirmation contract is missing: $confirmation_contract" >&2
    exit 1
  fi
done

python3 - "$ROOT_DIR" <<'PY'
from pathlib import Path
import sys

root = Path(sys.argv[1])
ordering_contracts = (
    (
        "test.py",
        "if not should_send_live(self.env):",
        'validate_live_recipient(self.env, payload["to"])',
        "missing = [",
        "client_factory = self.client_factory",
    ),
    (
        "test.js",
        "if (!shouldSendLive(env)) {",
        "validateLiveRecipient(env, payload.to);",
        "const missingCredentials = missingSettings",
        "const createClient = clientFactory",
    ),
)
for relative_path, dry_run, confirmation, credentials, client_setup in ordering_contracts:
    source = (root / relative_path).read_text(encoding="utf-8")
    positions = tuple(
        source.index(marker)
        for marker in (dry_run, confirmation, credentials, client_setup)
    )
    if positions != tuple(sorted(positions)):
        raise SystemExit(
            "{} must confirm the live recipient after the dry-run branch and "
            "before credential or client setup.".format(relative_path)
        )
PY

for e164_contract in \
  'E164_PHONE_PATTERN = re.compile(r"^\+[1-9][0-9]{1,14}$")' \
  'validate_phone(payload["to"], "TWILIO_TO")' \
  'validate_phone(payload["from"], "TWILIO_FROM")' \
  'const E164_PHONE_PATTERN = /^\+[1-9][0-9]{1,14}$/;' \
  "validatePhone(payload.to, 'TWILIO_TO')" \
  "validatePhone(payload.from, 'TWILIO_FROM')" \
  "test_phone_settings_must_use_e164" \
  "TWILIO_TO must be an E.164 phone number"; do
  if ! grep -Fq -- "$e164_contract" "$ROOT_DIR/test.py" && \
     ! grep -Fq -- "$e164_contract" "$ROOT_DIR/test.js" && \
     ! grep -Fq -- "$e164_contract" "$ROOT_DIR/tests/test_company_comms.py" && \
     ! grep -Fq -- "$e164_contract" "$ROOT_DIR/tests/test_js_contracts.js"; then
    printf '%s\n' "E.164 phone validation contract is missing: $e164_contract" >&2
    exit 1
  fi
done

for python_privacy_contract in \
  "class MessageValidationError(ValueError)" \
  "class CredentialValidationError(RuntimeError)" \
  "isinstance(error, SAFE_CLI_ERROR_TYPES)" \
  "test_cli_error_message_preserves_credential_validation_errors" \
  "test_cli_error_message_hides_unexpected_value_errors"; do
  if ! grep -Fq -- "$python_privacy_contract" "$ROOT_DIR/test.py" && \
     ! grep -Fq -- "$python_privacy_contract" "$ROOT_DIR/tests/test_company_comms.py"; then
    printf '%s\n' "Python CLI privacy contract is missing: $python_privacy_contract" >&2
    exit 1
  fi
done

for node_privacy_contract in \
  "class MessageValidationError extends Error" \
  "class CredentialValidationError extends Error" \
  "error instanceof MessageValidationError" \
  "new Error('Missing required Twilio credentials: auth-token-secret')"; do
  if ! grep -Fq -- "$node_privacy_contract" "$ROOT_DIR/test.js" && \
     ! grep -Fq -- "$node_privacy_contract" "$ROOT_DIR/tests/test_js_contracts.js"; then
    printf '%s\n' "Node.js CLI privacy contract is missing: $node_privacy_contract" >&2
    exit 1
  fi
done

for python_override_contract in \
  "def message_setting(override, env, name)" \
  "if override is None:" \
  "test_explicit_arguments_do_not_read_environment_fallbacks" \
  "test_explicit_blank_arguments_do_not_fall_back_to_environment" \
  "self.assertEqual(FakeTwilioClient.instances, [])"; do
  if ! grep -Fq -- "$python_override_contract" "$ROOT_DIR/test.py" && \
     ! grep -Fq -- "$python_override_contract" "$ROOT_DIR/tests/test_company_comms.py"; then
    printf '%s\n' "Python explicit override contract is missing: $python_override_contract" >&2
    exit 1
  fi
done

for override_doc in "$README" "$ROOT_DIR/SECURITY.md" "$ROOT_DIR/VISION.md"; do
  if ! grep -Fq "explicit" "$override_doc"; then
    printf '%s\n' "$override_doc must document explicit Python message overrides." >&2
    exit 1
  fi
done

WORKFLOW="$ROOT_DIR/.github/workflows/check.yml"

expected_workflow=$(cat <<'YAML'
name: Check

on:
  pull_request:
  push:
  workflow_dispatch:

permissions:
  contents: read

concurrency:
  group: check-${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  check:
    name: Python ${{ matrix.python }} / Node ${{ matrix.node }}
    runs-on: ubuntu-24.04
    timeout-minutes: 10
    strategy:
      fail-fast: false
      matrix:
        include:
          - python: "3.10"
            node: "20"
          - python: "3.12"
            node: "22"
          - python: "3.14"
            node: "24"
    steps:
      - name: Check out repository
        uses: actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10 # v6.0.3
        with:
          persist-credentials: false
      - name: Set up Python
        uses: actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405 # v6.2.0
        with:
          python-version: ${{ matrix.python }}
      - name: Set up Node.js
        uses: actions/setup-node@48b55a011bda9f5d6aeb4c2d9c7362e8dae4041e # v6.4.0
        with:
          node-version: ${{ matrix.node }}
      - name: Run repository checks
        run: make check
      - name: Verify external working directory
        run: cd "$(mktemp -d)" && make -C "$GITHUB_WORKSPACE" check
YAML
)

if [ "$(cat "$WORKFLOW")" != "$expected_workflow" ]; then
  printf '%s\n' "GitHub Actions workflow must match the fail-closed hosted verification contract." >&2
  exit 1
fi

for workflow_contract in \
  "permissions:" \
  "contents: read" \
  'group: check-${{ github.workflow }}-${{ github.ref }}' \
  "cancel-in-progress: true" \
  "runs-on: ubuntu-24.04" \
  "timeout-minutes: 10" \
  'python: "3.10"' \
  'python: "3.12"' \
  'python: "3.14"' \
  'node: "20"' \
  'node: "22"' \
  'node: "24"' \
  "actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10" \
  "actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405" \
  "persist-credentials: false" \
  "actions/setup-node@48b55a011bda9f5d6aeb4c2d9c7362e8dae4041e # v6.4.0" \
  "actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10 # v6.0.3" \
  "actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405 # v6.2.0" \
  "run: make check" \
  'run: cd "$(mktemp -d)" && make -C "$GITHUB_WORKSPACE" check'; do
  if ! grep -Fq -- "$workflow_contract" "$WORKFLOW"; then
    printf '%s\n' "GitHub Actions workflow is missing required contract: $workflow_contract" >&2
    exit 1
  fi
done

workflow_count=$(find "$ROOT_DIR/.github/workflows" -type f \( -name '*.yml' -o -name '*.yaml' \) | wc -l | tr -d ' ')
if [ "$workflow_count" -ne 1 ]; then
  printf '%s\n' ".github/workflows must contain only check.yml." >&2
  exit 1
fi

if grep -Eq 'uses: [^ ]+@(main|master|v[0-9]+)([[:space:]]|$)' "$WORKFLOW"; then
  printf '%s\n' "GitHub Actions must be pinned to immutable commit SHAs." >&2
  exit 1
fi

if ! grep -Fq '"$(ROOT)/scripts/check-baseline.sh"' "$MAKEFILE"; then
  printf '%s\n' "Makefile must run scripts/check-baseline.sh from make check." >&2
  exit 1
fi

for make_contract in \
  'ROOT := $(CURDIR)' \
  'cd "$(ROOT)" && $(PYTHON)' \
  'cd "$(ROOT)" && $(NODE)'; do
  if ! grep -Fq -- "$make_contract" "$MAKEFILE"; then
    printf '%s\n' "Makefile is missing root-independent contract: $make_contract" >&2
    exit 1
  fi
done

for node_exit_contract in \
  "process.exitCode = exitCode;" \
  "process.on('beforeExit'" \
  "assert.strictEqual(failedCliResult.status, 1)"; do
  if ! grep -Fq -- "$node_exit_contract" "$ROOT_DIR/test.js" && \
     ! grep -Fq -- "$node_exit_contract" "$ROOT_DIR/tests/test_js_contracts.js"; then
    printf '%s\n' "Node.js graceful exit contract is missing: $node_exit_contract" >&2
    exit 1
  fi
done

for target in "lint:" "test:" "build:" "package-check:" "verify:" "check:"; do
  if ! grep -Fq -- "$target" "$MAKEFILE"; then
    printf '%s\n' "Makefile must expose the $target gate." >&2
    exit 1
  fi
done

if [ "$(cat "$ROOT_DIR/requirements.txt")" != "twilio==9.10.9" ]; then
  printf '%s\n' "requirements.txt must pin twilio==9.10.9." >&2
  exit 1
fi

for dev_pin in "pip==26.1.2" "pip-audit==2.10.0"; do
  if ! grep -Fxq -- "$dev_pin" "$ROOT_DIR/requirements-dev.txt"; then
    printf '%s\n' "requirements-dev.txt is missing $dev_pin." >&2
    exit 1
  fi
done

for package_contract in \
  'env -u PYTHONPATH' \
  'importlib.metadata.version("twilio")' \
  'import importlib.metadata, sys, twilio' \
  '-m pip check' \
  '-m pip_audit -r "$ROOT_DIR/requirements.txt"'; do
  if ! grep -Fq -- "$package_contract" "$ROOT_DIR/scripts/check-python-package.sh"; then
    printf '%s\n' "Python package gate is missing: $package_contract" >&2
    exit 1
  fi
done

if [ "$(grep -Fc 'env -u PYTHONPATH' "$ROOT_DIR/scripts/check-python-package.sh")" -ne 4 ]; then
  printf '%s\n' "Every Python package-gate command must remove PYTHONPATH." >&2
  exit 1
fi

if ! grep -Fq 'PYTHON="$(PYTHON)" "$(ROOT)/scripts/check-python-package.sh"' "$MAKEFILE"; then
  printf '%s\n' "Makefile must run the isolated Python package gate." >&2
  exit 1
fi

for command in \
  "python3 -m unittest discover -s tests -p 'test_*.py'" \
  "node tests/test_js_contracts.js" \
  "make check" \
  "scripts/check-baseline.sh"; do
  if ! grep -Fq -- "$command" "$README"; then
    printf '%s\n' "README must document $command." >&2
    exit 1
  fi
done

for ignored in "__pycache__/" "*.py[cod]" "node_modules/" ".env" ".idea/" ".vscode/" "*.iml"; do
  if ! grep -Fq -- "$ignored" "$GITIGNORE"; then
    printf '%s\n' ".gitignore must include $ignored" >&2
    exit 1
  fi
done

tracked_editor_metadata=$(git -C "$ROOT_DIR" ls-files '.idea' '.vscode' '*.iml' || true)
if [ -n "$tracked_editor_metadata" ]; then
  printf '%s\n%s\n' "Local editor metadata must not be tracked:" "$tracked_editor_metadata" >&2
  exit 1
fi

found_plan=0
for plan in "$DOCS_PLANS"/*.md; do
  [ -e "$plan" ] || continue
  found_plan=1
  if ! grep -Fq "Status: Completed" "$plan"; then
    printf '%s\n' "$plan must record completed status." >&2
    exit 1
  fi
  if ! grep -Fq "make check" "$plan"; then
    printf '%s\n' "$plan must document make check verification." >&2
    exit 1
  fi
done

if [ "$found_plan" -eq 0 ]; then
  printf '%s\n' "docs/plans must contain completed markdown plans." >&2
  exit 1
fi
