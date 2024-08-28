#!/bin/bash

# Function to install Homebrew
install_homebrew() {
    echo "Homebrew not found. Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    if [[ $? -ne 0 ]]; then
        echo "Homebrew installation failed."
        exit 1
    fi
    echo "Homebrew installed successfully."
    eval "$(/opt/homebrew/bin/brew shellenv)"  # Ensure Homebrew is in the PATH (for Apple Silicon)
}

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    install_homebrew
else
    echo "Homebrew is already installed."
fi

# Run brew bundle
if [ -f "Brewfile" ]; then
    echo "Installing packages from Brewfile..."
    brew bundle
else
    echo "Brewfile not found in the current directory."
    exit 1
fi

echo "Installation completed."
