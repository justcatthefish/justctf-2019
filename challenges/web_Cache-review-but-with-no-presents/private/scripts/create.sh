#!/bin/bash

set -ex
name="$1"

mkdir -p "/home/justctf/tmp/$name"
chown "justctf:justctf" "/home/justctf/tmp/$name"
cd "/home/justctf/tmp/$name"

UNIX_SOCKET="/home/justctf/tmp/$name/sock.unix" /home/justctf/sandbox &>/dev/null &

echo "$!" > server.pid
