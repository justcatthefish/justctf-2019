#!/bin/bash

HOST=$1
SANDBOX=$2
curl -i "$HOST$SANDBOX/api/v1/report_meme" -X POST -d "url=http://127.0.0.1/$SANDBOX/api/v1/flag"
curl -i "$HOST$SANDBOX/api/v1/flag"

curl -i "$HOST$SANDBOX/api/v1/report_meme" -X POST -d "url=http://127.0.0.1/$SANDBOX/api/v1/flag?/$SANDBOX/api/v1/comments"
curl -i "$HOST$SANDBOX/api/v1/comments" -H "Accept-Language: en/$SANDBOX/api/v1/flag?,"
