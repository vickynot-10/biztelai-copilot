import json
import os
import urllib.error
import urllib.request
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

base_url = os.getenv("LLM_BASE_URL")
api_key = os.getenv("LLM_API_KEY")
model = os.getenv("LLM_MODEL")

print("base_url:", repr(base_url))
print("model:", repr(model))

print("\n--- raw request ---")
url = base_url.rstrip("/") + "/chat/completions"
body = json.dumps(
    {"model": model, "messages": [{"role": "user", "content": "Say OK"}]}
).encode()
request = urllib.request.Request(
    url,
    data=body,
    headers={"Content-Type": "application/json", "Authorization": "Bearer " + api_key},
)
print("POST", url)
try:
    with urllib.request.urlopen(request) as response:
        print(response.status, response.read()[:300])
except urllib.error.HTTPError as error:
    print(error.code, error.read()[:400])

print("\n--- openai sdk ---")
client = OpenAI(base_url=base_url, api_key=api_key)
try:
    reply = client.chat.completions.create(
        model=model, messages=[{"role": "user", "content": "Say OK"}]
    )
    print("WORKS:", reply.choices[0].message.content)
except Exception as error:
    print("FAILS:", repr(error))
    print("url:", getattr(getattr(error, "response", None), "url", None))
    print("body:", getattr(getattr(error, "response", None), "text", None))
