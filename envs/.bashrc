export GOPATH=$HOME/code/nav
export PATH=$PATH:$GOPATH/bin
export GOPRIVATE=git.nav.com

alias k="kubectl"
alias int1="kubectl config use-context int1"
alias int3="kubectl config use-context int3"
alias demo="kubectl config use-context demo"
alias prod="kubectl config use-context prod"

kssh() {
	pod=`kubectl get pods | grep "$1" | awk '{print $1}' | head -n 1`; kubectl exec -it --request-timeout=5s $pod bash
}

kgrep() { 
	k get pods | grep "$1" 
}

alias cov="go test ./... -coverprofile=coverage.out && go tool cover -html=coverage.out"


