iatest=$(expr index "$-" i)

#######################################################
# SOURCED ALIAS'S AND SCRIPTS
#######################################################

# Source global definitions
if [ -f /etc/bashrc ]; then
	. /etc/bashrc
fi

[ -f $HOME/.common.shrc ] && source $HOME/.common.shrc

# Enable bash programmable completion features in interactive shells
if [ -f /usr/share/bash-completion/bash_completion ]; then
	. /usr/share/bash-completion/bash_completion
elif [ -f /etc/bash_completion ]; then
	. /etc/bash_completion
fi

#######################################################
# EXPORTS
#######################################################

# Disable the bell
if [[ $iatest > 0 ]]; then bind "set bell-style visible"; fi

# Expand the history size
export HISTFILESIZE=10000
export HISTSIZE=10000

# Don't put duplicate lines in the history and do not add lines that start with a space
export HISTCONTROL=erasedups:ignoredups:ignorespace

# Check the window size after each command and, if necessary, update the values of LINES and COLUMNS
shopt -s checkwinsize

# Causes bash to append to history instead of overwriting it so if you start a new terminal, you have old session history
shopt -s histappend
PROMPT_COMMAND='history -a'

# Allow ctrl-S for history navigation (with ctrl-R)
[[ $- == *i* ]] && stty -ixon

# Ignore case on auto-completion
# Note: bind used instead of sticking these in .inputrc
if [[ $iatest > 0 ]]; then bind "set completion-ignore-case on"; fi

# Show auto-completion list automatically, without double tab
if [[ $iatest > 0 ]]; then bind "set show-all-if-ambiguous On"; fi

# Set the default editor
export VISUAL=vim
set -o vi

# To have colors for ls and all grep commands such as grep, egrep and zgrep
export CLICOLOR=1
export LS_COLORS='no=00:fi=00:di=00;36:ln=01;36:pi=40;33:so=01;35:do=01;35:bd=40;33;01:cd=40;33;01:or=40;31;01:ow=00;36:st=31;00:ex=01;32:*.tar=01;31:*.tgz=01;31:*.arj=01;31:*.taz=01;31:*.lzh=01;31:*.zip=01;31:*.z=01;31:*.Z=01;31:*.gz=01;31:*.bz2=01;31:*.deb=01;31:*.rpm=01;31:*.jar=01;31:*.jpg=01;35:*.jpeg=01;35:*.gif=01;35:*.bmp=01;35:*.pbm=01;35:*.pgm=01;35:*.ppm=01;35:*.tga=01;35:*.xbm=01;35:*.xpm=01;35:*.tif=01;35:*.tiff=01;35:*.png=01;35:*.mov=01;35:*.mpg=01;35:*.mpeg=01;35:*.avi=01;35:*.fli=01;35:*.gl=01;35:*.dl=01;35:*.xcf=01;35:*.xwd=01;35:*.ogg=01;35:*.mp3=01;35:*.wav=01;35:*.xml=00;31:'
#export GREP_OPTIONS='--color=auto'

# Color for manpages in less makes manpages a little easier to read
export LESS_TERMCAP_mb=$'\E[01;31m'
export LESS_TERMCAP_md=$'\E[01;31m'
export LESS_TERMCAP_me=$'\E[0m'
export LESS_TERMCAP_se=$'\E[0m'
export LESS_TERMCAP_so=$'\E[01;44;33m'
export LESS_TERMCAP_ue=$'\E[0m'
export LESS_TERMCAP_us=$'\E[01;32m'

#######################################################
# GENERAL ALIAS'S
#######################################################
# To temporarily bypass an alias, we preceed the command with a \
# EG: the ls command is aliased, but to use the normal ls command you would type \ls

# Change directory aliases
alias ..='cd ..'
alias ...='cd ../..'
alias ....='cd ../../..'
alias .....='cd ../../../..'

# cd into the old directory
alias back='cd "$OLDPWD"'

#######################################################
# Set the ultimate amazing command prompt
#######################################################

git-branch-name() {
	git symbolic-ref HEAD 2>/dev/null | cut -d"/" -f 3-8
}

git-branch-prompt() {
	local branch=$(git-branch-name)
	if [ $branch ]; then printf " [%s]" $branch; fi
}

## Define colors
#LIGHTGRAY="$(echo -e "\033[0;37m")"
#WHITE="$(echo -e "\033[1;37m")"
#BLACK="$(echo -e "\033[0;30m")"
#DARKGRAY="$(echo -e "\033[1;30m")"
#RED="$(echo -e "\033[0;31m")"
#LIGHTRED="$(echo -e "\033[1;31m")"
#GREEN="$(echo -e "\033[0;32m")"
#LIGHTGREEN="$(echo -e "\033[92m")"
#BROWN="$(echo -e "\033[0;33m")"
#YELLOW="$(echo -e "\033[33m")"
#LIGHTYELLOW="$(echo -e "\033[93m")"
#BLUE="$(echo -e "\033[0;34m")"
#LIGHTBLUE="$(echo -e "\033[1;34m")"
#MAGENTA="$(echo -e "\033[0;35m")"
#LIGHTMAGENTA="$(echo -e "\033[95m")"
#CYAN="$(echo -e "\033[0;36m")"
#LIGHTCYAN="$(echo -e "\033[96m")"
#NOCOLOR="$(echo -e "\033[0m")"

declare -A TRUELINE_SYMBOLS=(
	[git_modified]='✚'
	[git_github]=''
	[git_gitlab]=''
	[git_bitbucket]=''
	[git_ahead]='↑'
	[git_behind]='↓'
	[segment_separator]=''
	[working_dir_folder]='⋯'
	[working_dir_separator]=''
	[working_dir_home]='⌂'
	[newline]='❯'
	[clock]='🕒'
	[ssh]='⌁'
	[bg_jobs]='⏎'
	[read_only]=''
)
TRUELINE_SHOW_VIMODE=true
TRUELINE_WORKING_DIR_SPACE_BETWEEN_PATH_SEPARATOR=true
TRUELINE_VIMODE_CMD_CURSOR='under'
TRUELINE_VIMODE_INS_CURSOR='under'
[ ! -f ~/.trueline.sh ] && curl -s https://raw.githubusercontent.com/petobens/trueline/master/trueline.sh -o ~/.trueline.sh
source $HOME/.trueline.sh

command -v kubectl &>/dev/null && source <(kubectl completion bash)
command -v k9s &>/dev/null && source <(k9s completion bash)
command -v helm &>/dev/null && source <(helm completion bash)

if command -v fzf > /dev/null 2>&1; then
	eval "$(fzf --bash)"
fi

if [ -f ~/.asdf ]; then
	. $HOME/.asdf/asdf.sh
	. $HOME/.asdf/completions/asdf.bash
fi
