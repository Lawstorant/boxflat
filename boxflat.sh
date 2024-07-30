#! /usr/bin/env sh

COMMAND="python3 /usr/share/boxflat/entrypoint.py"

if [ "$FLATPAK_ID" = "io.github.lawstorant.boxflat" ]; then
    COMMAND="python3 /app/share/boxflat/entrypoint.py --flatpak"
fi

$COMMAND
