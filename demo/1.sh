#!/bin/sh

curl -sS "$SOCLAAS_BASE_URL/models" \
  -H "Authorization: Bearer $SOCLAAS_API_KEY" \
  -H "Content-Type: application/json" \
  | jq
