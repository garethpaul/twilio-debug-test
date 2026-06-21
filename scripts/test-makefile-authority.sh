#!/bin/sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd -P)
MAKEFILE=$ROOT_DIR/Makefile
TEMP_ROOT=$(mktemp -d "${TMPDIR:-/tmp}/twilio-debug-make-authority-XXXXXX")
trap 'rm -rf "$TEMP_ROOT"' EXIT HUP INT TERM
CONTROL_DIR=$TEMP_ROOT/control
ATTACKER_ROOT=$TEMP_ROOT/attacker
MARKER=$TEMP_ROOT/make-syntax-expanded
TOOL_LOG=$TEMP_ROOT/tool.log
mkdir -p "$CONTROL_DIR" "$ATTACKER_ROOT"

run_make() { (cd "$CONTROL_DIR" && /usr/bin/make --no-print-directory -f "$MAKEFILE" "$@"); }

fake_tool=$TEMP_ROOT/fake-tool
cat >"$fake_tool" <<EOF
#!/bin/sh
printf 'cwd=%s args=%s\n' "\$PWD" "\$*" >>"$TOOL_LOG"
exit 0
EOF
chmod +x "$fake_tool"

: >"$TOOL_LOG"
run_make lint ROOT="$ATTACKER_ROOT" PYTHON="$fake_tool" NODE="$fake_tool" >/dev/null
grep -F "$ROOT_DIR" "$TOOL_LOG" >/dev/null
if grep -F "$ATTACKER_ROOT" "$TOOL_LOG" >/dev/null; then echo "ROOT redirected verification" >&2; exit 1; fi

: >"$TOOL_LOG"
run_make lint SHELL=/bin/false PYTHON="$fake_tool" NODE="$fake_tool" >/dev/null
grep -F "$ROOT_DIR" "$TOOL_LOG" >/dev/null

: >"$TOOL_LOG"
run_make node-package-check NPM="$fake_tool" >/dev/null
grep -F 'ci --ignore-scripts --no-audit --fund=false' "$TOOL_LOG" >/dev/null
grep -F 'audit --omit=dev --audit-level=low' "$TOOL_LOG" >/dev/null

for tool in PYTHON NODE NPM; do
  rm -f "$MARKER"
  set +e
  run_make lint "$tool=\$(shell /usr/bin/touch '$MARKER')tool" >"$TEMP_ROOT/$tool.out" 2>"$TEMP_ROOT/$tool.err"
  status=$?
  set -e
  if [ "$status" -eq 0 ] || [ -e "$MARKER" ]; then echo "Make-syntax $tool was not rejected safely" >&2; exit 1; fi
  grep -F "$tool must be a literal executable path" "$TEMP_ROOT/$tool.err" >/dev/null
done

set +e
run_make lint MAKEFLAGS=--just-print >"$TEMP_ROOT/flags.out" 2>"$TEMP_ROOT/flags.err"; status=$?
set -e
if [ "$status" -eq 0 ]; then echo "MAKEFLAGS was not rejected" >&2; exit 1; fi
grep -F "MAKEFLAGS must not be overridden" "$TEMP_ROOT/flags.err" >/dev/null

startup=$TEMP_ROOT/startup.mk
printf '%s\n' 'STARTUP_FILE_LOADED := yes' >"$startup"
set +e
(cd "$CONTROL_DIR" && MAKEFILES="$startup" /usr/bin/make --no-print-directory -f "$MAKEFILE" lint) >"$TEMP_ROOT/startup.out" 2>"$TEMP_ROOT/startup.err"; status=$?
set -e
if [ "$status" -eq 0 ]; then echo "MAKEFILES was not rejected" >&2; exit 1; fi
grep -F "MAKEFILES must be empty" "$TEMP_ROOT/startup.err" >/dev/null

set +e
run_make lint PYTHON="$fake_tool" NODE="$fake_tool" MAKEFILE_LIST="$TEMP_ROOT/attacker.mk" >"$TEMP_ROOT/list.out" 2>"$TEMP_ROOT/list.err"; status=$?
set -e
if [ "$status" -eq 0 ]; then echo "MAKEFILE_LIST was not rejected" >&2; exit 1; fi
grep -F "MAKEFILE_LIST must not be overridden" "$TEMP_ROOT/list.err" >/dev/null

printf '%s\n' "Make authority tests passed: root, shell, Python, Node, npm, MAKEFLAGS, MAKEFILES, and MAKEFILE_LIST"
