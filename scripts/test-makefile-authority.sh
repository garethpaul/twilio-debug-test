#!/bin/sh
set -eu

ROOT_DIR=$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd -P)
MAKEFILE=$ROOT_DIR/Makefile
WRAPPER=$ROOT_DIR/scripts/run-make.sh
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

GNU_MAKE=${GNU_MAKE:-}
if [ -z "$GNU_MAKE" ] && command -v gmake >/dev/null 2>&1; then
  GNU_MAKE=$(command -v gmake)
fi

if [ -n "$GNU_MAKE" ]; then
  : >"$TOOL_LOG"
  "$GNU_MAKE" --no-print-directory -n \
    --eval='override MAKEFLAGS :=' \
    -f "$MAKEFILE" lint PYTHON="$fake_tool" NODE="$fake_tool" \
    >"$TEMP_ROOT/dry-run.out" 2>"$TEMP_ROOT/dry-run.err"
  if [ -s "$TOOL_LOG" ]; then
    echo "raw GNU Make dry-run bypass did not reproduce" >&2
    exit 1
  fi

  failing_tool=$TEMP_ROOT/failing-tool
  cat >"$failing_tool" <<'EOF'
#!/bin/sh
exit 1
EOF
  chmod +x "$failing_tool"
  "$GNU_MAKE" --no-print-directory -i \
    --eval='override MAKEFLAGS :=' \
    -f "$MAKEFILE" lint PYTHON="$failing_tool" NODE="$failing_tool" \
    >"$TEMP_ROOT/ignore-errors.out" 2>"$TEMP_ROOT/ignore-errors.err"

  : >"$TOOL_LOG"
  GNUMAKEFLAGS=-n "$GNU_MAKE" --no-print-directory \
    --eval='override MAKEFLAGS :=' \
    -f "$MAKEFILE" lint PYTHON="$fake_tool" NODE="$fake_tool" \
    >"$TEMP_ROOT/gnumakeflags.out" 2>"$TEMP_ROOT/gnumakeflags.err"
  if [ -s "$TOOL_LOG" ]; then
    echo "raw GNUMAKEFLAGS bypass did not reproduce" >&2
    exit 1
  fi
fi

startup_marker=$TEMP_ROOT/startup-executed
cat >"$startup" <<EOF
\$(shell /usr/bin/touch '$startup_marker')
override MAKEFILES :=
EOF
MAKEFILES="$startup" /usr/bin/make --no-print-directory \
  -f "$MAKEFILE" lint PYTHON="$fake_tool" NODE="$fake_tool" \
  >"$TEMP_ROOT/startup-exec.out" 2>"$TEMP_ROOT/startup-exec.err"
if [ ! -e "$startup_marker" ]; then
  echo "raw executable MAKEFILES bypass did not reproduce" >&2
  exit 1
fi

earlier=$TEMP_ROOT/earlier.mk
earlier_marker=$TEMP_ROOT/earlier-executed
cat >"$earlier" <<EOF
\$(shell /usr/bin/touch '$earlier_marker')
EOF
/usr/bin/make --no-print-directory -f "$earlier" -f "$MAKEFILE" \
  lint PYTHON="$fake_tool" NODE="$fake_tool" \
  >"$TEMP_ROOT/earlier.out" 2>"$TEMP_ROOT/earlier.err"
if [ ! -e "$earlier_marker" ]; then
  echo "raw earlier -f bypass did not reproduce" >&2
  exit 1
fi

later=$TEMP_ROOT/later.mk
later_marker=$TEMP_ROOT/later-executed
cat >"$later" <<EOF
\$(shell /usr/bin/touch '$later_marker')
EOF
/usr/bin/make --no-print-directory -f "$MAKEFILE" -f "$later" \
  lint PYTHON="$fake_tool" NODE="$fake_tool" \
  >"$TEMP_ROOT/later.out" 2>"$TEMP_ROOT/later.err"
if [ ! -e "$later_marker" ]; then
  echo "raw later -f bypass did not reproduce" >&2
  exit 1
fi

if [ ! -x "$WRAPPER" ]; then
  echo "sanitized Make wrapper is missing" >&2
  exit 1
fi

for rejected in '' 'test' '-n' '--eval=all:' 'ROOT=/tmp' 'lint extra'; do
  set +e
  if [ -z "$rejected" ]; then
    "$WRAPPER" >"$TEMP_ROOT/wrapper-reject.out" 2>"$TEMP_ROOT/wrapper-reject.err"
  elif [ "$rejected" = 'lint extra' ]; then
    "$WRAPPER" lint extra >"$TEMP_ROOT/wrapper-reject.out" 2>"$TEMP_ROOT/wrapper-reject.err"
  else
    "$WRAPPER" "$rejected" >"$TEMP_ROOT/wrapper-reject.out" 2>"$TEMP_ROOT/wrapper-reject.err"
  fi
  status=$?
  set -e
  if [ "$status" -eq 0 ]; then
    echo "wrapper accepted unsupported arguments: $rejected" >&2
    exit 1
  fi
done

: >"$TOOL_LOG"
PYTHON="$fake_tool" NODE="$fake_tool" "$WRAPPER" lint >/dev/null
grep -F "$ROOT_DIR" "$TOOL_LOG" >/dev/null

wrapper_marker=$TEMP_ROOT/wrapper-startup-executed
cat >"$startup" <<EOF
\$(shell /usr/bin/touch '$wrapper_marker')
EOF
: >"$TOOL_LOG"
MAKEFILES="$startup" \
MAKEFLAGS='--just-print' \
MFLAGS='-i' \
MAKEOVERRIDES='ROOT=/tmp' \
GNUMAKEFLAGS="--eval=\$(shell /usr/bin/touch '$wrapper_marker')" \
PYTHON="$fake_tool" NODE="$fake_tool" \
  "$WRAPPER" lint >/dev/null
if [ -e "$wrapper_marker" ]; then
  echo "wrapper allowed inherited Make startup authority" >&2
  exit 1
fi

mkdir -p "$ATTACKER_ROOT/scripts"
cat >"$ATTACKER_ROOT/Makefile" <<EOF
lint:
	@/usr/bin/touch '$TEMP_ROOT/attacker-makefile-executed'
EOF
ln -s "$WRAPPER" "$ATTACKER_ROOT/physical
"
ln -s "../physical
" "$ATTACKER_ROOT/scripts/run-make.sh"
: >"$TOOL_LOG"
PYTHON="$fake_tool" NODE="$fake_tool" \
  "$ATTACKER_ROOT/scripts/run-make.sh" lint >/dev/null
if [ -e "$TEMP_ROOT/attacker-makefile-executed" ]; then
  echo "wrapper symlink redirected repository root" >&2
  exit 1
fi
grep -F "$ROOT_DIR" "$TOOL_LOG" >/dev/null

printf '%s\n' "Make authority tests passed: raw bypasses reproduced and sanitized wrapper excluded them"
