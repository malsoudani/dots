#!/usr/bin/env bash
# Run the reference implementations' own commands.
# Skips a project cleanly when the tool it needs is not installed.
set -euo pipefail

here=$(cd "$(dirname "$0")" && pwd)
pkg=$(cd "$here/.." && pwd)
status=0
skipped=0

note() { printf '== %s\n' "$*"; }
skip() { printf 'skip: %s\n' "$*"; skipped=$((skipped + 1)); }
fail() { printf 'FAIL: %s\n' "$*" >&2; status=1; }

backend="$pkg/examples/backend"
frontend="$pkg/examples/frontend"

if command -v uv >/dev/null 2>&1; then
  note "backend: models and migrations agree"
  (cd "$backend" && uv run --no-project --with-requirements requirements.txt \
    python manage.py makemigrations --check --dry-run) || fail "backend migration check"
  note "backend: test suite"
  (cd "$backend" && uv run --no-project --with-requirements requirements.txt \
    python manage.py test) || fail "backend tests"
else
  skip "uv not found: backend checks"
fi

if command -v npm >/dev/null 2>&1; then
  if [ ! -d "$frontend/node_modules" ]; then
    note "frontend: install dependencies"
    (cd "$frontend" && npm install --no-audit --no-fund --no-package-lock) || fail "frontend install"
  fi
  note "frontend: typecheck"
  (cd "$frontend" && npm run --silent typecheck) || fail "frontend typecheck"
  note "frontend: test suite"
  (cd "$frontend" && npm test --silent) || fail "frontend tests"
else
  skip "npm not found: frontend checks"
fi

printf 'verify-examples: %d skipped, exit %d\n' "$skipped" "$status"
exit "$status"
