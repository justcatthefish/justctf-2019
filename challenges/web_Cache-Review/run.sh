#!/bin/sh

export FLAG=$(cat flag.txt)
echo "FLAG: $FLAG"
docker-compose -f private/docker-compose.yml rm --force --stop
docker-compose -f private/docker-compose.yml build
docker-compose -f private/docker-compose.yml up -d
