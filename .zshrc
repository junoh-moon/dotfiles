unsetopt BEEP	# disable bell

setopt correct
setopt globdots
setopt histignoredups
setopt pushd_to_home
setopt pushd_silent

VI_MODE_SET_CURSOR=false
ZSH_AUTOSUGGEST_USE_ASYNC=true
ZSH_DISABLE_COMPFIX=true # Disable 'zsh compinit insecure directoreis' warning

export PROMPT_EOL_MARK=''

# venv activate가 PROMPT를 건드리지 못하게 막음.
# oh-my-zsh의 virtualenvwrapper 플러그인이 starship init 전에 로드되어
# workon_cwd → activate가 zsh 기본 PROMPT를 _OLD_VIRTUAL_PS1에 저장한 뒤,
# 이후 cd 때 deactivate가 그 값으로 starship PROMPT를 덮어쓰는 문제 방지.
# venv 표시는 starship의 [python] 모듈이 대신함.
export VIRTUAL_ENV_DISABLE_PROMPT=1

autoload -Uz compinit
compinit

source $HOME/.common.shrc




[ ! -d "${HOME}/.zgenom" ] && git clone --depth 1 https://github.com/jandamm/zgenom.git "${HOME}/.zgenom"
source "${HOME}/.zgenom/zgenom.zsh" > /dev/null
source "${HOME}/.zgenom/zgen.zsh" > /dev/null

zgenom autoupdate --background

# Backup my aliases
local _save_aliases="$(alias -L)"

# if the init script doesn't exist
if ! zgen saved; then

  zgen oh-my-zsh

  zgen oh-my-zsh plugins/command-not-found
  zgen oh-my-zsh plugins/vi-mode
  zgen oh-my-zsh plugins/gradle
  zgen oh-my-zsh plugins/pip
  zgen oh-my-zsh plugins/virtualenvwrapper
  zgen oh-my-zsh plugins/asdf
  zgen oh-my-zsh plugins/poetry
  zgen oh-my-zsh plugins/gnu-utils

  zgen load lukechilds/zsh-better-npm-completion
  zgen load Aloxaf/fzf-tab
  zgen load zsh-users/zsh-syntax-highlighting
  zgen load zsh-users/zsh-history-substring-search
  zgen load zsh-users/zsh-autosuggestions
  zgen load zsh-users/zsh-completions
  zgen load RobSis/zsh-completion-generator		# compgen <program> to parse, and compinit then to apply
  zgen load IngoMeyer441/zsh-easy-motion


  # generate the init script from plugins above
  zgen save

  zgenom compile "$HOME/.zshrc"
fi

bindkey '^ ' autosuggest-accept

bindkey -M vicmd ',,' vi-easy-motion	# Bind ,, as a prefix key
bindkey -M vicmd -r ','					# Unbind ','


########################
#  My Configuration    #
########################

# Restore (override) my aliases
eval "$_save_aliases"
unset _save_aliases


# Disable commit-hash-sort when completing git checkout, diff, and so one.
zstyle ':completion:*:git-*:*' sort false

alias cd='pushd'
alias back='popd'


command -v kubectl &> /dev/null && source <(kubectl completion zsh)
command -v k9s &> /dev/null && source <(k9s completion zsh)
command -v helm &> /dev/null && source <(helm completion zsh)

if command -v fzf > /dev/null 2>&1; then
	source <(fzf --zsh)
fi

export STARSHIP_CONFIG="$HOME/.dotfiles/config/starship/starship.toml"
eval "$(starship init zsh)"
