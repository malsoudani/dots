#!/bin/bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BREW_SCRIPT="$ROOT_DIR/brew/brew_packages.sh"
BASH_SCRIPT="$ROOT_DIR/envs/setup_default_bash.sh"
LOCAL_BIN="$HOME/.local/bin"

GIT_USER_NAME="Mohamed Alsoudani"
GIT_USER_EMAIL="mr.hassuny@gmail.com"

run_step() {
  local title="$1"
  echo
  echo "==> $title"
}

setup_vscode_cli() {
  if command -v code >/dev/null 2>&1; then
    echo "VS Code CLI already available: $(command -v code)"
    return
  fi

  local code_bin=""

  if [[ -x "/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code" ]]; then
    code_bin="/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code"
  elif [[ -x "$HOME/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code" ]]; then
    code_bin="$HOME/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code"
  fi

  if [[ -z "$code_bin" ]]; then
    echo "VS Code app not found in standard locations."
    echo "Install VS Code and rerun setup_machine.sh."
    return 1
  fi

  mkdir -p "$LOCAL_BIN"
  ln -sf "$code_bin" "$LOCAL_BIN/code"
  echo "Linked code CLI: $LOCAL_BIN/code -> $code_bin"
}

if ! command -v git >/dev/null 2>&1; then
  echo "git is required but was not found on PATH."
  exit 1
fi

chmod +x "$BREW_SCRIPT" "$BASH_SCRIPT"

run_step "Install Homebrew and Brewfile packages"
"$BREW_SCRIPT"

run_step "Setup bash profile files and default shell"
"$BASH_SCRIPT"

run_step "Configure global git identity"
git config --global user.name "$GIT_USER_NAME"
git config --global user.email "$GIT_USER_EMAIL"

echo "Configured git identity:"
echo "  user.name=$(git config --global --get user.name)"
echo "  user.email=$(git config --global --get user.email)"

run_step "Setup VS Code CLI in terminal PATH"
setup_vscode_cli

echo
echo "Setup complete. Open a new terminal session to pick up all changes."
