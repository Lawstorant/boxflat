#! /usr/bin/env bash

# SITE_PACKAGES=$(python3 -c 'import site; print(site.getsitepackages()[0])')

# if [[ -z "${SITE_PACKAGES}" ]]; then
#     echo "Site packages not found"
#     exit 1
# fi

PREFIX=""

# uninstall boxflat
if [[ $1 == "remove" ]]; then
    rm "/usr/share/applications/boxflat.desktop"
    rm "/usr/bin/boxflat"
    rm -rf "/usr/share/boxflat"
    # rm -rf "$SITE_PACKAGES/boxflat"
    exit 0
fi

# mkdir -p "$SITE_PACKAGES/boxflat"
# cp -r boxflat/* "$SITE_PACKAGES/boxflat"
mkdir -p "/usr/share/boxflat"
cp -r ./* "/usr/share/boxflat/"
cp --preserve=mode "boxflat.sh" "/usr/bin/boxflat"
cp "boxflat.desktop" "/usr/share/applications/"
