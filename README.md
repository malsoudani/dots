# dots

my developement configurations live here


## New machine setup

1. Install all Homebrew packages from this repo:

  ```sh
  chmod +x brew/brew_packages.sh
  ./brew/brew_packages.sh
  ```

2. Install default bash profile files and set bash as your default shell:

  ```sh
  chmod +x envs/setup_default_bash.sh
  ./envs/setup_default_bash.sh
  ```

3. In VS Code, install the `code` CLI command once:

  - Open Command Palette
  - Run: Shell Command: Install 'code' command in PATH

This repo's `ff` fzf function opens selected files in VS Code using `code -r`.
