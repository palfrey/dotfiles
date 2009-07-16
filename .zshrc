# .zshrc

# User specific aliases and functions

# Source global definitions
if [ -f /etc/zshrc ]; then
	source /etc/zshrc
fi

HOST=`hostname`
DOMAIN=`hostname -d`

if [ -f ~/.zshrc-$HOST-colours ]; then
	source ~/.zshrc-$HOST-colours
elif [ -f ~/.zshrc-colours ]; then
	source ~/.zshrc-colours
fi

if [ -f ~/.zshrc-$HOST ]; then
	source ~/.zshrc-$HOST
fi
if [ -f ~/.zshrc-$DOMAIN ]; then
    source ~/.zshrc-$DOMAIN
fi

if [ -f /usr/games/fortune ]; then
	/usr/games/fortune
fi

alias pine='pine -d 0'
alias pico='pico -w'

if [ -d ~/bin ]; then
	export PATH=~/bin:$PATH
fi

setopt PROMPT_SUBST
export PROMPT="$RED%n$NO_COLOUR@$GREEN%m:${RED}[$LIGHT_CYAN%~${RED}]$NO_COLOUR "
export RPS1="%(?.$LIGHT_CYAN.$GREEN<=====)$NO_COLOUR"

export HISTSIZE=5000
export HISTFILE=~/.history
export SAVEHIST=5000

export NO_LIST_BEEP=1
export COMPLETE_IN_WORD=1

case $TERM in 
	xterm*|rxvt)
		precmd () { print -Pn "\e]0;%n@%m: %~\a" }
		preexec () { print -Pn "\e]0;%n@%m: $1\a" }
	;;
	screen*)
		precmd () { print -Pn "\e]0;screen - %n@%m: %~\a" }
		preexec () { print -Pn "\e]0;screen - %n@%m: $1\a" }
	;;
esac

bindkey '\e[1~' beginning-of-line
bindkey '\e[4~' end-of-line
case $TERM in (xterm*)
	bindkey '\e[H' beginning-of-line
	bindkey '\e[F' end-of-line ;;
esac

alias sane='echo -e "\\033c";tput is2;stty sane line 1'

# if a glob doesn't match, just hand it to the command unchanged
unsetopt nomatch

# ignore history duplicates
setopt histignoredups

alias ind='indent -kr -bap -bl -bli0 -nce -cdw -cli4 -bls -ut -ts4 -l300'
alias m2u='tr "\015" "\012" <'

# set Emacs binding for line edit, as that gives Home/End as normal.
# Vi mapping is a pain for single-line editing
bindkey -e

alias ls='ls --color=auto -F'
alias sc='screen -R'
alias scl='screen -ls'
alias j='jobs'
alias np='nautilus "`pwd`"'

export DEBFULLNAME=Tom\ Parker
export DEBEMAIL=debian@tevp.net

# drop caps lock entirely
xmodmap -e "remove lock = Caps_Lock"

# searching for specified string
bindkey "^R"    history-incremental-search-backward
