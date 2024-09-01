#!/bin/bash

export DEBUG="false"

if ! [ -n "$CF_TURNSTILE_SECRET" ] || ! [ -n "$CF_TURNSTILE_SITE_KEY" ]; then

printf "Error: Cloudflare keys not set\n"
exit 1

fi

if ! [[ -n "$SECRET" ]]; then

printf "Error: No secret set\n"
exit 1

fi

if ! [[ -n "$COMMENTS" ]]; then

printf "Error: Comments value not set\n"
exit 1

fi

if ![[-n "$RATE_LIMIT"]]; then

printf "Error: No rate limit set\n"
exit 1

fi

docker compose build
docker compose up -d
