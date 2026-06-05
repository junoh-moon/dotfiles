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

# User vendor completions, loaded by compinit as fpath functions.
#
# Self-healing cache: each tool's `completion zsh` output is written once to
# $zsh_completion_path/_<tool> and reused, so startup pays no subprocess cost.
#   - Generated automatically on first run when the cache file is missing.
#   - Regenerated when the tool binary is newer than the cache (covers brew/
#     OrbStack upgrades, which drop a new binary with a fresh mtime).
#   - Caveat: invalidation is mtime-based, so version-manager shims (asdf/mise),
#     whose shim file never changes, can go stale. Force a refresh with:
#         rm ~/.local/share/zsh/vendor-completions/_*
# The anonymous function () keeps the loop's locals out of the global scope.
zsh_completion_path="$HOME/.local/share/zsh/vendor-completions"
[ -d "$zsh_completion_path" ] || mkdir -p "$zsh_completion_path"
() {
	local tool bin out cache
	for tool in kubectl k9s helm; do
		bin=${commands[$tool]:A}   # resolved real path (follows symlinks) for accurate mtime
		[ -n "$bin" ] || continue
		cache="$zsh_completion_path/_$tool"
		if [[ ! -s "$cache" || "$bin" -nt "$cache" ]]; then
			# Capture first; only overwrite the cache on success + non-empty
			# output, so a failed run never truncates a good cache (-> stale).
			out=$("$tool" completion zsh 2>/dev/null) && [[ -n "$out" ]] \
				&& print -r -- "$out" >| "$cache"
		fi
	done
}
case ":$FPATH:" in
	*":$zsh_completion_path:"*) ;;
	*) fpath=("$zsh_completion_path" "${fpath[@]}") ;;
esac
unset zsh_completion_path

autoload -Uz compinit
# Rebuild the completion dump at most once per day. On every other startup,
# `compinit -C` skips both the security audit (compaudit) and the dump
# regeneration (compdump, ~380ms), reusing the cached ~/.zcompdump as-is.
# The glob must run in an array assignment, not inside [[ ]] (which performs no
# filename generation): qualifier (N.mh+24) yields ~/.zcompdump only when it is
# a plain file older than 24h, so an empty array means the dump is still fresh.
() {
	local -a stale=("$HOME/.zcompdump"(N.mh+24))
	if (( $#stale )); then
		compinit
	else
		compinit -C
	fi
}

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


# kubectl/k9s/helm completions are cached as fpath functions near compinit (top of file).

if command -v fzf > /dev/null 2>&1; then
	source <(fzf --zsh)
fi

export STARSHIP_CONFIG="$HOME/.dotfiles/config/starship/starship.toml"
eval "$(starship init zsh)"
