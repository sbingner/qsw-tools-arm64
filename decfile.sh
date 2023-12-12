#!/bin/sh
set -e

keyhex="2a77737174707972"

decfile() {
    inf=$1
    tmpf="/tmp/dec.tmp"
    if openssl enc -provider legacy < /dev/null; then
        openssl enc -d -des-ecb -K $keyhex -in $inf -out $tmpf  -provider legacy -provider default || return 1
    else
        openssl enc -d -des-ecb -K $keyhex -in $inf -out $tmpf || return 1
    fi
    mv $tmpf $inf
}

decfile "$1"
