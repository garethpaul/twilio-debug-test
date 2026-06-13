#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
PYTHON=${PYTHON:-python3}
VENV_DIR=$(mktemp -d "${TMPDIR:-/tmp}/twilio-debug-python.XXXXXX")

cleanup() {
  rm -rf "$VENV_DIR"
}
trap cleanup EXIT

"$PYTHON" -m venv "$VENV_DIR"
PACKAGE_PYTHON="$VENV_DIR/bin/python"

env -u PYTHONPATH "$PACKAGE_PYTHON" -m pip install \
  --disable-pip-version-check \
  -r "$ROOT_DIR/requirements.txt" \
  -r "$ROOT_DIR/requirements-dev.txt"

env -u PYTHONPATH "$PACKAGE_PYTHON" -c \
  'import importlib.metadata, sys, twilio; actual = importlib.metadata.version("twilio"); expected = sys.argv[1]; assert actual == expected, "expected twilio %s, got %s" % (expected, actual)' \
  9.10.9
env -u PYTHONPATH "$PACKAGE_PYTHON" -m pip check
env -u PYTHONPATH "$PACKAGE_PYTHON" -m pip_audit -r "$ROOT_DIR/requirements.txt"
