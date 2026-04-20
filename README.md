# dots

my developement configurations live here


## New machine setup

1. Run the master setup script:

  ```sh
  chmod +x setup_machine.sh
  ./setup_machine.sh
  ```

This script will:

- Install Homebrew and Brewfile packages
- Link bash profile files and switch default shell to bash
- Configure global git name/email
- Add VS Code CLI (`code`) to your terminal by linking it into `~/.local/bin`

2. Or run setup steps individually:

Install all Homebrew packages from this repo:

  ```sh
  chmod +x brew/brew_packages.sh
  ./brew/brew_packages.sh
  ```

Install default bash profile files and set bash as your default shell:

  ```sh
  chmod +x envs/setup_default_bash.sh
  ./envs/setup_default_bash.sh
  ```

This repo's `ff` fzf function opens selected files in VS Code using `code -r`.
