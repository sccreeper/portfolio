#!/bin/bash

export DEBUG="false"

if ! [[ -n "$SECRET" ]]; then

echo "Error: No secret set"
exit 1

fi

if ! [[ -n "$COMMENTS" ]]; then

printf "Error: Comments value not set"
exit 1

fi

docker-compose build
docker-compose up -d
