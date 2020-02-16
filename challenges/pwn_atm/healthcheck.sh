#!/bin/sh

# Run e.g. as:
# HOST=localhost PORT=1337
#
# Can add 'DEBUG' for debugging mode

IMG="disconnect3d/pwntools:3.13.0-ubuntu18.04"
CMD="python /solv/exploit.py $*"
docker run -it \
    --rm \
    --net=host \
    -v `pwd`/solv:/solv \
    --workdir /solv \
    $IMG $CMD
