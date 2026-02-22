#!/bin/bash
# Auto-sudo script that handles password automatically
# Usage: ./auto-sudo.sh command [args]

set -euo pipefail

if [ "$#" -eq 0 ]; then
    echo "Usage: auto-sudo <command> [args...]" >&2
    exit 2
fi

# First check if we can use sudo without password (thanks to our NOPASSWD config)
if sudo -n true 2>/dev/null; then
    # We can use sudo without password
    sudo "$@"
else
    # Fall back to autoexpect when sudo prompts interactively.
    if command -v autoexpect >/dev/null 2>&1; then
        autoexpect "sudo $*"
    else
        echo "autoexpect not found. Please install accessibility package correctly." >&2
        exit 1
    fi
fi
