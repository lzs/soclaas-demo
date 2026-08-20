#!/usr/bin/env python

from openai import OpenAI
import os

# Instantiate client pointing to SoCLaaS Gateway
client = OpenAI(
    base_url=f"{os.environ['SOCLAAS_BASE_URL']}",
    api_key=os.environ["SOCLAAS_API_KEY"],
)

response = client.chat.completions.create(
    model=os.environ["SOCLAAS_MODEL"], # qwen3.6:35b
    messages=[
        {"role": "user", "content": "Say hello in one sentence."}
    ],
)

print(response.choices[0].message.content)
