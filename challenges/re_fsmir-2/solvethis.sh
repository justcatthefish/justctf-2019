#!/bin/sh
docker run --rm -v $(pwd):/data -w /data rweda/verilator "cd solv; ./build.sh"

