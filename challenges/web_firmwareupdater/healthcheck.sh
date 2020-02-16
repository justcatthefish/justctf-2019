#!/bin/sh
set -x
# Run as: ./healthcheck.sh IP_OR_DOMAIN

IMG="web-firmwareupdater-solver"
docker build -t $IMG -f solv/Dockerfile solv

docker run -it \
    --rm \
    --net=host \
    $IMG \
    bash -c "/solv/solver.sh $*"

