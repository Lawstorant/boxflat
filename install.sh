#! /usr/bin/env bash

PREFIX=""

# uninstall boxflat
if [[ $1 == "remove" ]]; then
    rm "/usr/share/applications/boxflat.desktop"
    rm "/usr/bin/boxflat"
    rm -rf "/usr/share/boxflat"
    rm /etc/udev/rules.d/99-moza-racing.rules
    exit 0
fi

mkdir -p "/usr/share/boxflat"
cp -r ./boxflat "/usr/share/boxflat/"
cp -r ./data "/usr/share/boxflat/"
cp -r ./udev "/usr/share/boxflat/"
cp entrypoint.py "/usr/share/boxflat/"

cp --preserve=mode "boxflat.sh" "/usr/bin/boxflat"
cp boxflat.desktop "/usr/share/applications/"
cp udev/99-moza-racing.rules "/etc/udev/rules.d/"

# refresh udev so the rules take effect immadietely
udevadm control --reload
udevadm trigger --attr-match=subsystem=tty
