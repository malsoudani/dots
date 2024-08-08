# Mo's terminal scripts

This directory contains the following utilities to manage and facilitate the installation, startup, and symlink creation of Python scripts using Docker and Python:

1. `reviewboard_utility.py`
2. `add_to_path.py`
3. `setup_symlinks.sh`

## Utilities Overview

### `reviewboard_utility.py`

A command-line utility for installing, starting, and stopping Review Board using Docker Compose.

**Commands:**
- `install [file_location]`: Installs Review Board using Docker Compose. Defaults to the current directory if no location is provided.
- `start [file_location]`: Starts the Review Board service. Defaults to the current directory if no location is provided.
- `stop [file_location]`: Stops the Review Board service. Defaults to the current directory if no location is provided.

### `add_to_path.py`

A script to add a specified Python script to the system PATH by creating a symlink in the user's local bin directory.

**Usage:**
\`\`\`sh
python add_to_path.py <script_path>
\`\`\`

### `setup_symlinks.sh`

A bash script that checks if Python is installed, and if it is, it takes all the Python utilities in the current directory and creates a symlink for them using the `add_to_path.py` command.

**Usage:**
\`\`\`sh
./setup_symlinks.sh
\`\`\`

## Setup Instructions

1. Ensure all scripts are in the same directory.
2. Make `setup_symlinks.sh` executable:
   \`\`\`sh
   chmod +x setup_symlinks.sh
   \`\`\`
3. Run the setup script:
   \`\`\`sh
   ./setup_symlinks.sh
   \`\`\`

This will create symlinks for all Python scripts in the current directory, allowing you to run them without the `.py` extension.

