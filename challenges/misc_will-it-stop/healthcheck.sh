#!/bin/sh

# Run e.g. as:
# HOST=localhost PORT=1337

# Port to which the task will be exposed
IMG="disconnect3d/pwntools:3.13.0-ubuntu18.04"
CMD="python2 /solv/solve.py $*"
docker run -it \
    --rm \
    --net=host \
    -v `pwd`/solv:/solv \
    --workdir /solv \
    $IMG $CMD
