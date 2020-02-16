#!/bin/sh

HOST=${1-localhost}
PORT=${2-1337}
RETRIES=${3-5}

for i in {1..$RETRIES}; do
    flag=$(./poc.py $HOST $PORT | tail -n1)
    if [ $? -eq 0 ]; then
        echo "$flag"
        exit 0
    fi
done

exit 1;




