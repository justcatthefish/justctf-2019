#!/bin/bash

docker build -t web-ugly-website .
docker run \
    -d \
    -e FLAG1 \
    -e FLAG2 \
    -e SECRET_KEY \
    -e ADMIN_TOKEN \
    -e CODE_ADMIN \
    -e CODE_USER \
    -e RECAPTCHA_SITE_KEY \
    -e RECAPTCHA_SECRET_KEY \
    -e BOT_URL \
    -e CHALLENGE_BASEURL \
    -e PRODUCTION \
    -e BOT_EASY_TIMEOUT \
    -e BOT_HARD_TIMEOUT \
    -p 127.0.0.1:8888:8080 \
    --restart=unless-stopped \
    --cap-drop=all \
    -t web-ugly-website