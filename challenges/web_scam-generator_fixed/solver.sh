#!/bin/bash

export FLAG=$(cat flag.txt)
export TASK_ENVS=$(cat environ.json)
echo "FLAG: $FLAG"
echo -e "ENVS:\n$TASK_ENVS"

docker build --build-arg TASK_ENVS -t web-scam-generator-solver solv
docker run --rm -p 127.0.0.1:3337:8080 -it web-scam-generator-solver