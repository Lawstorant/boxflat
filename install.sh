#! /usr/bin/env bash

PREFIX=""
if [[ $1 == "add-prefix" ]]; then
    PREFIX="$2"
fi

# uninstall boxflat
if [[ $1 == "remove" || $3 == "remove" ]]; then
    rm "$PREFIX/usr/share/applications/boxflat.desktop"
    rm "$PREFIX/usr/bin/boxflat"
    rm -rf "$PREFIX/usr/share/boxflat"
    cp -r ./icons/* "$PREFIX/usr/share/icons/hicolor/"
    rm "$PREFIX/etc/udev/rules.d/"*boxflat*.rules
    exit 0
fi

if [[ -n $PREFIX ]]; then
    mkdir -p "$PREFIX/etc/udev/rules.d"
    mkdir -p "$PREFIX/usr/bin"
    mkdir -p "$PREFIX/usr/share/applications"
fi

mkdir -p "$PREFIX/usr/share/boxflat"
mkdir -p "$PREFIX/usr/share/icons/hicolor/"

cp -r ./boxflat "$PREFIX/usr/share/boxflat/"
cp -r ./data "$PREFIX/usr/share/boxflat/"
cp -r ./icons/* "$PREFIX/usr/share/icons/hicolor/"
cp -r ./udev "$PREFIX/usr/share/boxflat/"
cp entrypoint.py "$PREFIX/usr/share/boxflat/"

cp --preserve=mode "boxflat.sh" "$PREFIX/usr/bin/boxflat"
cp boxflat.desktop "$PREFIX/usr/share/applications/"
cp udev/* "$PREFIX/etc/udev/rules.d/"

# refresh udev so the rules take effect immadietely
if [[ $1 == "no-udev" || $3 == "no-udev" ]]; then
    exit 0
fi

udevadm control --reload
udevadm trigger --attr-match=subsystem=tty
