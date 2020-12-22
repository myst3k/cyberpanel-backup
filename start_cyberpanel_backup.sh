#!/usr/bin/env bash

if test -f "/etc/cyberpanel/.b2_env"; then
    source /etc/cyberpanel/.b2_env
    echo "Found and loaded Backblaze B2 Environment File"
    BACKBLAZE=true
fi

if test -f "/etc/cyberpanel/.wasabi_env"; then
    source /etc/cyberpanel/.wasabi_env
    echo "Found and loaded Wasabi Environment File"
    WASABI=true
fi

/opt/scripts/cyberpanel_backup.py "$@"