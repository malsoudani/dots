ff () {
  start_path="$1"
  dir=$(ls -1);

    if [[ -z "$start_path" ]]; then
      files=$(ls -1 $(findr $PWD '.' 2>/dev/null | \
                      fzf --multi --height 80% --reverse --preview 'cat {}' | \
                      perl -ne 'chomp $_; print $_ . " "'))
      echo $files;
      if [[ "$dir" =~ "$files" ]]; then
        return;
      fi
      vim $files
    else
      files=$(ls -1 $(findr $start_path '.' 2>/dev/null | \
                      fzf --multi --height 80% --reverse --preview 'cat {}' | \
                      perl -ne 'chomp $_; print $_ . " "'))
      if [[ "$dir" =~ "$files" ]]; then
        return;
      fi
      vim $files
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
    find $path -regextype posix-extended -regex ".*$file_name";
  else
    ag "." -lG $file_name $path
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
