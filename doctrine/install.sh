#!/usr/bin/env bash
# Bootstrap installer for Doctrine.
#
#   curl -fsSL https://raw.githubusercontent.com/malsoudani/dots/master/doctrine/install.sh | bash -s -- <doctrine args>
#
# Run from a checkout, it runs the local bin/doctrine. Otherwise it clones or
# fast-forwards the repository, links the CLI into a bin directory, and runs it.
set -euo pipefail

REPO_URL=${DOCTRINE_REPO_URL:-https://github.com/malsoudani/dots.git}
REF=${DOCTRINE_REF:-master}
HOME_DIR=${DOCTRINE_HOME:-$HOME/.local/share/doctrine}
BIN_DIR=${DOCTRINE_BIN_DIR:-$HOME/.local/bin}

say() { printf '%s\n' "$*" >&2; }
die() { printf 'install.sh: error: %s\n' "$*" >&2; exit 1; }

# Run from a checkout: the CLI sits next to this script.
script_dir=$(cd "$(dirname "$0")" 2>/dev/null && pwd) || script_dir=""
if [ -n "$script_dir" ] && [ -x "$script_dir/bin/doctrine" ]; then
  exec "$script_dir/bin/doctrine" "$@"
fi

command -v git >/dev/null 2>&1 || die "git is required"
command -v python3 >/dev/null 2>&1 || die "python3 is required"
python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)' \
  || die "python3 3.9 or newer is required"

if [ -d "$HOME_DIR/.git" ]; then
  say "updating $HOME_DIR"
  git -C "$HOME_DIR" fetch --quiet --depth 1 origin "$REF"
  git -C "$HOME_DIR" merge --quiet --ff-only FETCH_HEAD \
    || say "note: could not fast-forward; keeping the current checkout"
else
  say "cloning $REPO_URL into $HOME_DIR"
  git clone --quiet --depth 1 --branch "$REF" "$REPO_URL" "$HOME_DIR"
fi

cli="$HOME_DIR/doctrine/bin/doctrine"
[ -f "$cli" ] || die "the repository has no doctrine/bin/doctrine"
chmod +x "$cli" 2>/dev/null || true

mkdir -p "$BIN_DIR"
link="$BIN_DIR/doctrine"
if [ -L "$link" ] || [ -e "$link" ]; then
  if [ -L "$link" ] && [ "$(readlink "$link")" = "$cli" ]; then
    : # This link already points at the managed checkout.
  else
    die "$link already exists and is not a Doctrine-managed symlink; move it aside first"
  fi
else
  ln -s "$cli" "$link"
fi

case ":$PATH:" in
  *":$BIN_DIR:"*) ;;
  *) say "note: add $BIN_DIR to your PATH to run 'doctrine' directly" ;;
esac

if [ "$#" -eq 0 ]; then
  "$cli" agents
  say ""
  say "next: install the rules into your agent, for example 'doctrine install --agent claude'"
  exit 0
fi

exec "$cli" "$@"
