#!/bin/sh

export SECRET="123456"
export DEBUG="true"
export COMMENTS="true"

docker-compose build
docker-compose up -d