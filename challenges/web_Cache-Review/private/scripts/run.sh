#!/bin/bash

/scripts/iptables.sh
service nginx restart

su -l justctf -pc '/home/justctf/manager'
