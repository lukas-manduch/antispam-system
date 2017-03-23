#! /bin/bash

while [[ $# -ge 1 ]] ; do
    echo "Sending" "$1"
    python sender.py "$1"
    shift
    done
