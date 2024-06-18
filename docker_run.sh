#!/bin/bash

export DEBUG="false"

if ! [[ -n "$SECRET" ]]; then

echo "Error: No secret set"
exit 1

else

docker-compose build
docker-compose up -d

fi