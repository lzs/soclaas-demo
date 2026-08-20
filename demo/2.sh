#!/bin/sh

curl -sS "$SOCLAAS_BASE_URL/chat/completions" \
  -H "Authorization: Bearer $SOCLAAS_API_KEY" \
  -H "Content-Type: application/json" \
  --data @- <<EOM | jq
{
    "model": "$SOCLAAS_MODEL",
    "messages": [
         {"role": "system", "content": "Be concise."},
         {"role": "user", "content": "Define API gateway."}
    ]
}
EOM
