#!/bin/bash

set -ex
name="$1"

pkill --pidfile "/home/justctf/tmp/$name/server.pid"
rm -rf "/home/justctf/tmp/$name"
