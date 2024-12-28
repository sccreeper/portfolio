#!/bin/sh

if [ "$DEBUG" == "true" ]; then
    echo "Running in debug mode"
    poetry run python3 -m src.app
else
    echo "Not running in debug mode"
    poetry run python3 -m gunicorn -b 0.0.0.0:8000 src.app:app
fi