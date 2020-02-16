#!/bin/sh

# Run e.g. as:
# HOST=localhost PORT=1337
#
# Can add 'DEBUG' for debugging mode

# Port to which the task will be exposed
IMG="disconnect3d/pwntools:3.13.0-ubuntu18.04"
CMD="python /solv/poc.py $*"
docker run -it \
    --net=host \
    -v `pwd`/solv:/solv \
    --workdir /solv \
    $IMG $CMD
