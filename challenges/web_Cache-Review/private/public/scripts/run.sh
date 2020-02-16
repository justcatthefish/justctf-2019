#!/bin/bash

./scripts/iptables.sh
service nginx restart

./bot &>/dev/stdout &
./meme
