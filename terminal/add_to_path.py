import os
import sys
import subprocess

def add_to_path(script_path, symlink_name):
    # Determine the path to the user's bin directory (usually ~/.local/bin or ~/bin)
    bin_dir = os.path.expanduser("~/.local/bin")
    if not os.path.exists(bin_dir):
        os.makedirs(bin_dir)

    # Create a symlink in the bin directory without the .py extension
    symlink_path = os.path.join(bin_dir, symlink_name)
    if os.path.exists(symlink_path):
        os.remove(symlink_path)

    os.symlink(script_path, symlink_path)
    print(f"Symlink created: {symlink_path} -> {script_path}")

    # Add bin_dir to PATH if it's not already included
    shell_profile = os.path.expanduser("~/.bashrc")
    if not os.path.exists(shell_profile):
        shell_profile = os.path.expanduser("~/.profile")
    with open(shell_profile, 'a') as f:
        f.write(f'\nexport PATH="$PATH:{bin_dir}"\n')

    # Source the shell profile to update the PATH
    subprocess.run(["source", shell_profile], shell=True)
    print(f"Added {bin_dir} to PATH. Please restart your terminal or run 'source {shell_profile}' to update the PATH.")

def main():
    if len(sys.argv) != 2:
        print("Usage: python add_to_path.py <script_path>")
        sys.exit(1)

    script_path = os.path.abspath(sys.argv[1])
    if not os.path.isfile(script_path):
        print(f"Error: {script_path} is not a valid file.")
        sys.exit(1)

    script_name = os.path.basename(script_path).replace('.py', '')
    # Ensure the script is executable
    os.chmod(script_path, 0o755)
    add_to_path(script_path, script_name)

if __name__ == "__main__":
    main()

