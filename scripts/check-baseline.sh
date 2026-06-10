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
  "SECURITY.md" \
  "VISION.md" \
  "test.js" \
  "test.py" \
  "tests/test_company_comms.py" \
  "tests/test_docs_plans.py" \
  "tests/test_js_contracts.js" \
  "docs/plans/2026-06-08-twilio-debug-test-baseline.md" \
  "docs/plans/2026-06-09-scripted-baseline-check.md" \
  "docs/plans/2026-06-10-ci-runtime-matrix.md" \
  "docs/plans/2026-06-10-cli-output-privacy.md" \
  "docs/plans/2026-06-10-python-cli-error-allowlist.md" \
  "scripts/check-baseline.sh"; do
  require_file "$path"
done

for python_privacy_contract in \
  "class MessageValidationError(ValueError)" \
  "class CredentialValidationError(RuntimeError)" \
  "isinstance(error, SAFE_CLI_ERROR_TYPES)" \
  "test_cli_error_message_hides_unexpected_value_errors"; do
  if ! grep -Fq -- "$python_privacy_contract" "$ROOT_DIR/test.py" && \
     ! grep -Fq -- "$python_privacy_contract" "$ROOT_DIR/tests/test_company_comms.py"; then
    printf '%s\n' "Python CLI privacy contract is missing: $python_privacy_contract" >&2
    exit 1
  fi
done

WORKFLOW="$ROOT_DIR/.github/workflows/check.yml"

for workflow_contract in \
  "permissions:" \
  "contents: read" \
  "branches:" \
  "- main" \
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
  "actions/setup-node@48b55a011bda9f5d6aeb4c2d9c7362e8dae4041e # v6.4.0" \
  "actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10 # v6.0.3" \
  "actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405 # v6.2.0" \
  "run: make check"; do
  if ! grep -Fq -- "$workflow_contract" "$WORKFLOW"; then
    printf '%s\n' "GitHub Actions workflow is missing required contract: $workflow_contract" >&2
    exit 1
  fi
done

if grep -Eq 'uses: [^ ]+@(main|master|v[0-9]+)([[:space:]]|$)' "$WORKFLOW"; then
  printf '%s\n' "GitHub Actions must be pinned to immutable commit SHAs." >&2
  exit 1
fi

if ! grep -Fq '"$(ROOT)/scripts/check-baseline.sh"' "$MAKEFILE"; then
  printf '%s\n' "Makefile must run scripts/check-baseline.sh from make check." >&2
  exit 1
fi

for make_contract in \
  'ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))' \
  'cd "$(ROOT)" && $(PYTHON)' \
  'cd "$(ROOT)" && $(NODE)'; do
  if ! grep -Fq -- "$make_contract" "$MAKEFILE"; then
    printf '%s\n' "Makefile is missing root-independent contract: $make_contract" >&2
    exit 1
  fi
done

for target in "lint:" "test:" "build:" "verify:" "check:"; do
  if ! grep -Fq -- "$target" "$MAKEFILE"; then
    printf '%s\n' "Makefile must expose the $target gate." >&2
    exit 1
  fi
done

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
