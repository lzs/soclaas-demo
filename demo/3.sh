#!/bin/sh

curl -sS -N "$SOCLAAS_BASE_URL/chat/completions" \
  -H "Authorization: Bearer $SOCLAAS_API_KEY" \
  -H "Content-Type: application/json" \
  -d @- <<EOM
{
    "model": "$SOCLAAS_MODEL",
    "messages": [
      {"role": "user", "content": "List 3 embedding uses."}
    ],
    "stream": true
}
EOM

