#!/bin/bash
# Script to automatically provide input for commands
# Usage: ./autoinput.sh [input] command [args]
# Example: ./autoinput.sh "yes" apt install package
# Example: ./autoinput.sh "password" sudo -S command

INPUT="$1"
shift

echo "$INPUT" | "$@" 