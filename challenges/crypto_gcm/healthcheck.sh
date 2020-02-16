#!/bin/sh

# Run e.g. as:
# HOST=localhost PORT=1337

cd solv
IMG="crypto-gcm-solver"
docker build -t $IMG .

CMD="sage solve.sage $*"
docker run -it \
    --rm \
    --net=host \
    $IMG $CMD
