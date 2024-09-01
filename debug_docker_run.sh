#!/bin/sh

export SECRET="123456"
export DEBUG="true"
export COMMENTS="true"

export RATE_LIMIT="50"

export CF_TURNSTILE_SECRET="1x0000000000000000000000000000000AA"
export CF_TURNSTILE_SITE_KEY="1x00000000000000000000AA"

docker compose build
docker compose up -d
