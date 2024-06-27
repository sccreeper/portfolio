#!/bin/sh

export SECRET="123456"
export DEBUG="true"
export COMMENTS="true"
export ADMIN_PASS="password"

docker-compose build
docker-compose up -d