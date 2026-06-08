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

# completion.zsh (loaded below) stores its completion cache under $ZSH_CACHE_DIR;
# ~/.local/share/zsh already exists (the vendor dir below lives under it).
ZSH_CACHE_DIR="$HOME/.local/share/zsh"

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

# Pre-empt sdkman's compinit. `.common.shrc` -> `.shinit` sources sdkman-init.sh,
# which runs its OWN `compinit` unless `compdef` is already defined. We want a
# single compinit that runs AFTER every plugin fpath is registered (far below),
# so install a tiny queuing stub now: sdkman and the plugins then see `compdef`
# defined and their calls are collected, to be flushed once the real compinit has
# run. Without this, sdkman compinits early -- before plugin fpaths exist -- and
# we pay a second compinit.
typeset -ga _compdef_queue
if ! typeset -f compdef >/dev/null; then
	# Quote each argument so the replayed `eval "compdef $c"` (below) preserves
	# argument boundaries -- bashcompinit registers `compdef '_bash_complete -o
	# default -F _sdk' sdk`, whose first arg must stay a single word.
	compdef() { _compdef_queue+=("${(j: :)${(q)@}}") }
fi

source $HOME/.common.shrc




[ ! -d "${HOME}/.zgenom" ] && git clone --depth 1 https://github.com/jandamm/zgenom.git "${HOME}/.zgenom"
source "${HOME}/.zgenom/zgenom.zsh" > /dev/null
source "${HOME}/.zgenom/zgen.zsh" > /dev/null

zgenom autoupdate --background

# Don't let zgenom bake its own `compinit` into init.zsh -- we run the single
# compinit ourselves below (after all fpaths are registered). Without this,
# zgenom defaults the flag on (compinit hasn't run yet) and we'd get two.
ZGEN_AUTOLOAD_COMPINIT=0

# Backup my aliases (OMZ libs/plugins below may clobber ls/ll/mkdir/...)
local _save_aliases="$(alias -L)"

# if the init script doesn't exist
if ! zgen saved; then

  # oh-my-zsh master (oh-my-zsh.sh) is intentionally NOT loaded -- it only
  # pulled in prompt libraries (git/vcs_info/theme/spectrum/...) that died when
  # the prompt moved to starship. Load just the libs whose side effects we use.
  zgen oh-my-zsh lib/history.zsh         # HISTSIZE/SAVEHIST/HISTFILE, share_history
  zgen oh-my-zsh lib/key-bindings.zsh    # arrows / Home / End / Del, Ctrl-x Ctrl-e
  zgen oh-my-zsh lib/completion.zsh      # case-insensitive match, menu select, colors
  zgen oh-my-zsh lib/directories.zsh     # auto_pushd, `...`, `la`
  zgen oh-my-zsh lib/functions.zsh       # omz_urlencode etc. (used by misc.zsh)
  zgen oh-my-zsh lib/misc.zsh            # interactivecomments, multios
  zgen oh-my-zsh lib/clipboard.zsh       # clipcopy/clippaste for vi-mode yank

  # plugins. Dropped:
  #  - asdf: Node moved to mise; vim's elixir build sources ~/.asdf/asdf.sh
  #    directly, so the interactive-shell plugin is unused.
  #  - poetry: rarely used, and its plugin re-generates _poetry asynchronously on
  #    every startup (truncating the file), which races our single compinit.
  zgen oh-my-zsh plugins/command-not-found
  zgen oh-my-zsh plugins/vi-mode
  zgen oh-my-zsh plugins/gradle
  zgen oh-my-zsh plugins/pip
  zgen oh-my-zsh plugins/virtualenvwrapper
  zgen oh-my-zsh plugins/gnu-utils

  zgen load lukechilds/zsh-better-npm-completion
  zgen load zsh-users/zsh-completions
  zgen load RobSis/zsh-completion-generator		# compgen <program> to parse, and compinit then to apply
  zgen load IngoMeyer441/zsh-easy-motion

  # generate the init script from plugins above
  zgen save

  zgenom compile "$HOME/.zshrc"
fi

# Every plugin fpath is now registered (from the cached init.zsh, or just loaded
# above), so run the single compinit -- the one the sdkman stub deferred to.
# `-u` rescans fpath (so a newly cached vendor completion binds on the next
# shell) and rebuilds the dump when the function count changes. Note: `-u` does
# NOT skip compaudit (only `-C` does); the -u flag just uses any insecure dirs
# without prompting. We don't gate `-C` on the dump's mtime: compinit doesn't
# refresh that mtime on a cache hit, so such a gate degrades to `-u` after a day
# anyway -- not worth the complexity for ~7ms.
autoload -Uz compinit
compinit -u -d "$HOME/.zcompdump"
# Apply the compdef calls the stub queued before compinit defined the real one.
# (compinit has already replaced the stub `compdef` with the real function.)
() {
	local c
	for c in "$_compdef_queue[@]"; do eval "compdef $c"; done
}
unset _compdef_queue

# fzf-tab and the ZLE-widget-wrapping plugins MUST load after compinit (above):
# fzf-tab first, then the widget wrappers, with syntax-highlighting last.
zgen load Aloxaf/fzf-tab
zgen load zsh-users/zsh-history-substring-search
zgen load zsh-users/zsh-autosuggestions
zgen load zsh-users/zsh-syntax-highlighting

bindkey '^ ' autosuggest-accept

bindkey -M vicmd ',,' vi-easy-motion	# Bind ,, as a prefix key
bindkey -M vicmd -r ','					# Unbind ','


########################
#  My Configuration    #
########################

# Restore (override) my aliases
eval "$_save_aliases"
unset _save_aliases


# Color completion listings (and fzf-tab candidates) by $LS_COLORS. oh-my-zsh.sh
# (master) did this at its end -- `[[ -z "$LS_COLORS" ]] || zstyle ... list-colors
# "${(s.:.)LS_COLORS}"` -- overriding the empty `list-colors ''` that lib/
# completion.zsh sets. Dropping OMZ master dropped that line, so restore it here
# (after completion.zsh loads; .shinit has already populated LS_COLORS via dircolors).
[[ -z "$LS_COLORS" ]] || zstyle ':completion:*' list-colors "${(s.:.)LS_COLORS}"

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
