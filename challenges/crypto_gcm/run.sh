#!/bin/bash

PORT=${1-1337}

cd private
TASK="crypto-gcm"
docker build -t ${TASK} .

docker run -d \
    --name ${TASK} \
    --restart=always \
    --cap-drop=all \
    --cap-add=CHOWN \
    --cap-add=SETUID \
    --cap-add=SETGID \
    --cap-add=AUDIT_WRITE \
    --cap-add=SYS_ADMIN \
    --security-opt apparmor=unconfined \
    --security-opt seccomp=unconfined \
    -p $PORT:1337 \
    ${TASK}
