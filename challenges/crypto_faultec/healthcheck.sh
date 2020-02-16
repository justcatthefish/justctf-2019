#!/bin/sh

# Run e.g. as:
# HOST=localhost PORT=1337
#
# Can add 'DEBUG' for debugging mode

cd solv
IMG="crypto-faultec"
CMD="python3 solv.py"
docker build -t $IMG .

docker run -it \
    --rm \
    --net=host \
    --workdir /solv \
    $IMG $CMD $*
