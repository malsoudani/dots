#!/usr/bin/env bash
# Run every check for this package. Non-zero exit on any failure.
set -euo pipefail

here=$(cd "$(dirname "$0")" && pwd)
pkg=$(cd "$here/.." && pwd)
status=0

note() { printf '== %s\n' "$*"; }
fail() { printf 'FAIL: %s\n' "$*" >&2; status=1; }
run() {
  note "$*"
  if ! "$@"; then
    fail "$*"
  fi
}

run python3 -m unittest discover -s "$here" -t "$here"

if [ -x /usr/bin/python3 ]; then
  default_python=$(python3 -c 'import sys; print(sys.executable)')
  system_python=$(/usr/bin/python3 -c 'import sys; print(sys.executable)')
  if [ "$default_python" != "$system_python" ]; then
    run /usr/bin/python3 -m unittest discover -s "$here" -t "$here"
  fi
fi

run "$pkg/bin/doctrine" lint
run "$pkg/bin/doctrine" build --check

if command -v shellcheck >/dev/null 2>&1; then
  run shellcheck "$pkg/install.sh" "$here/run.sh" "$here/verify-examples.sh"
else
  note "shellcheck not found; skipping"
fi

if [ "$status" -ne 0 ]; then
  printf 'tests/run.sh: failed\n' >&2
fi
exit "$status"