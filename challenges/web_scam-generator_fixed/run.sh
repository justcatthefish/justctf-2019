#!/bin/bash

export FLAG=$(cat flag.txt)
export TASK_ENVS=$(cat environ.json)
echo "FLAG: $FLAG"
echo -e "ENVS:\n$TASK_ENVS"


docker-compose -f docker-compose.yml rm --force --stop
docker-compose -f docker-compose.yml build
docker-compose -f docker-compose.yml up -d
