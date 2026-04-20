ff () {
  local start_path="${1:-$PWD}"
  local selection

  selection=$(findr "$start_path" '.' 2>/dev/null | \
              fzf --multi --height 80% --reverse --preview 'cat {}') || return

  [[ -z "$selection" ]] && return

  if command -v code >/dev/null 2>&1; then
    while IFS= read -r file; do
      [[ -n "$file" ]] && code -r "$file"
    done <<< "$selection"
  else
    echo "VS Code CLI not found. Install the 'code' command from VS Code."
  fi
}

findr () {
  if [[ "$1" =~ "--help" ]]; then
      echo "findr PATH_HERE FILE_NAME";
      return;
  fi

  path=$1;
  file_name=$2;
  if [[ $(hostname) =~ beta|i0|my0|www0 ]]; then
    find "$path" -regextype posix-extended -regex ".*$file_name";
  else
    if command -v ag >/dev/null 2>&1; then
      ag "." -lG "$file_name" "$path"
    else
      rg --files "$path" | rg "$file_name"
    fi
  fi;
}

function homestead() {
    ( cd ~/Homestead && vagrant $* )
}

if [ -f "$(brew --prefix)/opt/bash-git-prompt/share/gitprompt.sh" ]; then
  __GIT_PROMPT_DIR=$(brew --prefix)/opt/bash-git-prompt/share
  GIT_PROMPT_ONLY_IN_REPO=1
  source "$(brew --prefix)/opt/bash-git-prompt/share/gitprompt.sh"
fi

export GOROOT=/usr/local/go
export GOPATH=/Users/malsoudani/repos
export PATH=$GOPATH/bin:$GOROOT/bin:$PATH
