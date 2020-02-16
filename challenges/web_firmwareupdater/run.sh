#!/bin/bash
export FLAG=$(cat flag.txt)
echo "FLAG: $FLAG"

TASK="web-firmwareupdater"

docker rm --force $TASK
docker build -t $TASK --build-arg FLAG=${FLAG} -f private/Dockerfile private

docker run -d \
   --restart unless-stopped \
   -p 80:80 \
   --cap-drop all \
   --cap-add NET_BIND_SERVICE \
   --security-opt=no-new-privileges \
   --ulimit nproc=20 \
   --ulimit nofile=50 \
    $TASK
