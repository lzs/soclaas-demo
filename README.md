# SoCLaaS demo

SoCLaaS (SoC LLM-as-a-Service) gives the National University of Singapore School of Computing community free access to large language model APIs for teaching, learning, experimentation, prototypes, and projects.

This repository is a small, practical starting point. It includes examples for discovering available models, making chat-completion requests, streaming responses, using the OpenAI-compatible Python SDK, and configuring OpenCode.

## Prerequisites

Before running an example, request access to SoCLaaS and choose a model available to your account.

### Get an API key

Log in to one of SoC's main Unix servers and issue a key:

```sh
soclaas-portal issue
```

If you have already issued a key and need to replace it, run:

```sh
soclaas-portal issue --rotate
```

The script offers to add the SoCLaaS environment variables to `~/.bashrc`. If you accept and want to use SoCLaaS in the current shell straight away, reload that file before continuing:

```sh
source ~/.bashrc
```

After you receive the key, store it only in a local environment variable or another approved secret store. Do not commit it to source control or include it in shared configuration files.

### Other Tools

You will need:

- `curl` and [`jq`](https://jqlang.org/) for the shell examples
- Python 3 and the `openai` package for the Python example

`curl`, `jq`, and Python 3 are already installed in SoC Unix servers. You will need the `openai` Python package instlled in your own environment.

## Configure your environment

Set the gateway URL, API key, and model once in your shell:

```sh
export SOCLAAS_BASE_URL="https://soclaas-api.comp.nus.edu.sg/v1"
export SOCLAAS_API_KEY="your-api-key"
export SOCLAAS_MODEL="qwen3.6:35b"
```

The above is typically setup for you via `~/.bashrc` by the `soclaas-portal issue` command.

To confirm the models available to you, run:

```sh
./demo/1.sh
```

You can choose another model by setting `SOCLAAS_MODEL` to a model identifier returned by the above call.

## Getting help

If you need access, have questions about model availability, or encounter service error, contact SoC Technical Services. Please note that Technical Services typically does not provide help on programming and development questions, e.g. debugging your program, explain how to use an API, how to configure a 3rd party tool, etc.
