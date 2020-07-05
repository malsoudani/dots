source ~/.bashrc

ff () {

  start_path="$1"
  dir=$(ls -1);

    if [[ -z "$start_path" ]]; then
      files=$(ls -1 $(findr $PWD '.' 2>/dev/null | \
                      fzf --multi --height 80% --reverse --preview 'bat --style=numbers --color=always {} | head -500' | \
                      perl -ne 'chomp $_; print $_ . " "'))
      echo $files;
      if [[ "$dir" =~ "$files" ]]; then
        return;
      fi
      emacs $files
    else
      files=$(ls -1 $(findr $start_path '.' 2>/dev/null | \
                      fzf --multi --height 80% --reverse --preview 'bat --style=numbers --color=always {} | head -500' | \
                      perl -ne 'chomp $_; print $_ . " "'))
      if [[ "$dir" =~ "$files" ]]; then
        return;
      fi
      emacs $files
    fi
}

findr () {
  if [[ "$1" =~ "--help" ]]; then
      echo "findr PATH_HERE FILE_NAME";
      return;
  fi
  path=$1;
  file_name=$2;
  ag "." -lG $file_name $path
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
