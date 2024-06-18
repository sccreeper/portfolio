#!/bin/sh

export DEBUG="false"

if ! [[ -v $SECRET ]]; then

echo "Error: No secret set"
exit 1

else

docker-compose build
docker-compose up -d

fi