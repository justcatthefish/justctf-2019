#!/bin/bash

export GUNICORN_WORKERS="${GUNICORN_WORKERS:-8}"
gunicorn server:app \
    --capture-output \
    --access-logfile access.log \
    --enable-stdio-inheritance \
    --workers ${GUNICORN_WORKERS} \
    --log-level debug \
    --bind 0.0.0.0:8080
