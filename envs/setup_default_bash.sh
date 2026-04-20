#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_BASH_PROFILE="$HOME/.bash_profile"
TARGET_BASHRC="$HOME/.bashrc"

link_file() {
  local src="$1"
  local dst="$2"

  if [[ -L "$dst" ]]; then
    rm "$dst"
  elif [[ -e "$dst" ]]; then
    mv "$dst" "${dst}.backup.$(date +%Y%m%d%H%M%S)"
  fi

  ln -s "$src" "$dst"
  echo "Linked $dst -> $src"
}

link_file "$SCRIPT_DIR/.bash_profile" "$TARGET_BASH_PROFILE"
link_file "$SCRIPT_DIR/.bashrc" "$TARGET_BASHRC"

if [[ "$SHELL" != "/bin/bash" ]]; then
  echo "Setting default shell to /bin/bash..."
  chsh -s /bin/bash
  echo "Default shell changed. Open a new terminal session."
else
  echo "Default shell already set to /bin/bash."
fi

echo "Bash profile setup complete."
