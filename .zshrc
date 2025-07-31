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

autoload -Uz compinit
compinit

source $HOME/.common.shrc

# Enable Powerlevel10k instant prompt. Should stay close to the top of ~/.zshrc.
# Initialization code that may require console input (password prompts, [y/n]
# confirmations, etc.) must go above this block; everything else may go below.
if [[ -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]]; then
  source "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"
fi



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
  zgen load romkatv/powerlevel10k powerlevel10k
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

# To customize prompt, run `p10k configure` or edit ~/.p10k.zsh.
[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh

