#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BREWFILE_PATH="$SCRIPT_DIR/Brewfile"

detect_brew() {
    if command -v brew >/dev/null 2>&1; then
        command -v brew
        return
    fi

    if [[ -x /opt/homebrew/bin/brew ]]; then
        echo "/opt/homebrew/bin/brew"
        return
    fi

    if [[ -x /usr/local/bin/brew ]]; then
        echo "/usr/local/bin/brew"
        return
    fi
}

# Function to install Homebrew
install_homebrew() {
    echo "Homebrew not found. Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    echo "Homebrew installed successfully."
}

set_bash_default_shell() {
    local desired_shell="/bin/bash"

    if [[ "$SHELL" == "$desired_shell" ]]; then
        echo "Default shell is already $desired_shell."
        return
    fi

    if grep -q "^$desired_shell$" /etc/shells; then
        echo "Setting default shell to $desired_shell..."
        chsh -s "$desired_shell"
        echo "Default shell updated. Open a new terminal session to use it."
    else
        echo "Could not verify $desired_shell in /etc/shells. Skipping shell change."
    fi
}

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    install_homebrew
else
    echo "Homebrew is already installed."
fi

BREW_BIN="$(detect_brew)"
if [[ -z "${BREW_BIN:-}" ]]; then
    echo "Homebrew installation failed: brew binary not found after install."
    exit 1
fi

eval "$("$BREW_BIN" shellenv)"

# Run brew bundle
if [ -f "$BREWFILE_PATH" ]; then
    echo "Installing packages from Brewfile..."
    brew bundle --file "$BREWFILE_PATH"
else
    echo "Brewfile not found at: $BREWFILE_PATH"
    exit 1
fi

if command -v ag >/dev/null 2>&1; then
    echo "ag is installed: $(command -v ag)"
else
    echo "ag is not available after brew bundle."
    exit 1
fi

set_bash_default_shell

echo "Installation completed."
