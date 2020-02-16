#!/bin/bash

docker build -t terjanq/web_ugly_website_solver ./solv
docker run \
    -e SOLVER_DOMAIN \
    -e CHALLENGE_BASEURL \
    -e ADMIN_TOKEN \
    -e SOLVER_WHAT \
    --rm -p 1337:8888 -it terjanq/web_ugly_website_solver