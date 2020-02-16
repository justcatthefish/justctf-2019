#!/bin/bash

./scripts/iptables.sh
service nginx restart

./meme
