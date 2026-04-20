source ~/.bashrc

# Load Homebrew into PATH for both Apple Silicon and Intel macOS.
if [[ -x /opt/homebrew/bin/brew ]]; then
  eval "$(/opt/homebrew/bin/brew shellenv)"
elif [[ -x /usr/local/bin/brew ]]; then
  eval "$(/usr/local/bin/brew shellenv)"
fi

ff () {
  local start_path="${1:-$PWD}"
  local selection

  selection=$(findr "$start_path" '.' 2>/dev/null | \
              fzf --multi --height 80% --reverse --preview 'bat --style=numbers --color=always {} | head -500') || return

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
  if command -v ag >/dev/null 2>&1; then
    ag "." -lG "$file_name" "$path"
  else
    rg --files "$path" | rg "$file_name"
  fi
} 

# search a directory and cd into it
dd() {
  local dir
  dir=$(find ${1:-.} -path '*/\.*' -prune \
                  -o -type d -print 2> /dev/null | fzf +m) &&
  cd "$dir"
}

########### git fzf
# checkout branches in git
bb() {
  local branches branch
  branches=$(git --no-pager branch -vv) &&
  branch=$(echo "$branches" | fzf +m) &&
  git checkout $(echo "$branch" | awk '{print $1}' | sed "s/.* //")
}

# fgst - pick files from `git status -s` 
is_in_git_repo() {
  git rev-parse HEAD > /dev/null 2>&1
}

fgst() {
  # "Nothing to see here, move along"
  is_in_git_repo || return

  local cmd="${FZF_CTRL_T_COMMAND:-"command git status -s"}"

  eval "$cmd" | FZF_DEFAULT_OPTS="--height ${FZF_TMUX_HEIGHT:-40%} --reverse $FZF_DEFAULT_OPTS $FZF_CTRL_T_OPTS" fzf -m "$@" | while read -r item; do
    echo "$item" | awk '{print $2}'
  done
  echo
}

############# docker fzf
# Select a docker container to start and attach to
function da() {
  local cid
  cid=$(docker ps -a | sed 1d | fzf -1 -q "$1" | awk '{print $1}')

  [ -n "$cid" ] && docker start "$cid" && docker attach "$cid"
}
# Select a running docker container to stop
function ds() {
  local cid
  cid=$(docker ps | sed 1d | fzf -q "$1" | awk '{print $1}')

  [ -n "$cid" ] && docker stop "$cid"
}
# Select a docker container to remove
function drm() {
  local cid
  cid=$(docker ps -a | sed 1d | fzf -q "$1" | awk '{print $1}')

  [ -n "$cid" ] && docker rm "$cid"
}

if [ -f "$(brew --prefix)/opt/bash-git-prompt/share/gitprompt.sh" ]; then
  __GIT_PROMPT_DIR=$(brew --prefix)/opt/bash-git-prompt/share
  GIT_PROMPT_ONLY_IN_REPO=1
  source "$(brew --prefix)/opt/bash-git-prompt/share/gitprompt.sh"
fi
export PATH="/usr/local/opt/postgresql@11/bin:$PATH"
export GOBIN="$GOPATH/bin"

eval "$(rbenv init -)"
