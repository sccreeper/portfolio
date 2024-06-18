#!/bin/sh

echo "$DEBUG"

if [ "$DEBUG" == "true" ]; then
    poetry run python3 -m src.app
else
    poetry run python3 -m gunicorn -b 0.0.0.0:8000 src.app:app
fi