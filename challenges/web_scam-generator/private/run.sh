#!/bin/bash

export SECRET_KEY=$(< /dev/urandom tr -dc _A-Z-a-z-0-9 | head -c32)
export GUNICORN_WORKERS="${GUNICORN_WORKERS:-12}"
gunicorn wsgi:app \
    --capture-output \
    --access-logfile access.log \
    --enable-stdio-inheritance \
    --workers ${GUNICORN_WORKERS} \
    --log-level debug \
    --bind 0.0.0.0:8080
