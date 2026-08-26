# SoCLaaS REST API with curl

These examples call the OpenAI-compatible SoCLaaS API directly. Set the
environment variables first (see the repository [README](../README.md)):

```sh
export SOCLAAS_BASE_URL="https://soclaas-api.comp.nus.edu.sg/v1"
export SOCLAAS_API_KEY="your-api-key"
export SOCLAAS_MODEL="qwen3.8:27b"
```

All requests authenticate with a bearer token. Replace `SOCLAAS_MODEL` with a
model returned by the models endpoint if necessary.

## List available models

```sh
curl --silent --show-error "$SOCLAAS_BASE_URL/models" \
  --header "Authorization: Bearer $SOCLAAS_API_KEY" \
  --header "Content-Type: application/json" | jq
```

## Basic chat completion

`/chat/completions` returns one JSON response when `stream` is omitted or set
to `false`.

```sh
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
```

To print only the generated text, use `jq` to select the first choice:

```sh
curl -sS "$SOCLAAS_BASE_URL/chat/completions" \
  --header "Authorization: Bearer $SOCLAAS_API_KEY" \
  --header "Content-Type: application/json" \
  --data '{
    "model": "'"$SOCLAAS_MODEL"'",
    "messages": [{"role": "user", "content": "Say hello in one sentence."}]
  }' | jq --raw-output '.choices[0].message.content'
```

## Continue a conversation

Send prior turns again with each request; chat-completion APIs are stateless.

```sh
curl --silent --show-error "$SOCLAAS_BASE_URL/chat/completions" \
  --header "Authorization: Bearer $SOCLAAS_API_KEY" \
  --header "Content-Type: application/json" \
  --data '{
    "model": "'"$SOCLAAS_MODEL"'",
    "messages": [
      {"role": "user", "content": "Give me one fun fact about octopuses."},
      {"role": "assistant", "content": "Octopuses have three hearts."},
      {"role": "user", "content": "Explain why they need them in one sentence."}
    ]
  }' | jq --raw-output '.choices[0].message.content'
```

## Stream a chat completion

Set `stream` to `true` and use `--no-buffer` (`-N`) so `curl` prints each
server-sent event as it arrives. The response uses `data:` lines and ends with
`data: [DONE]`.

```sh
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
```

## Send a request body from a file

For longer prompts, save a request as `request.json`. This avoids shell
quoting and makes the exact HTTP body easy to inspect or share without the API
key. Replace the example model identifier with one available to your account.

```json
{
  "model": "qwen3.8:27b",
  "messages": [
    {
      "role": "user",
      "content": "Write a haiku about software engineering."
    }
  ]
}
```

Then send it with `curl`:

```sh
curl --silent --show-error "$SOCLAAS_BASE_URL/chat/completions" \
  --header "Authorization: Bearer $SOCLAAS_API_KEY" \
  --header "Content-Type: application/json" \
  --data @request.json | jq --raw-output '.choices[0].message.content'
```
