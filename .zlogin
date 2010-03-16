if [[ "x$DISPLAY" != "x" ]]; then
	# drop caps lock entirely
	xmodmap -e "remove lock = Caps_Lock"
fi
