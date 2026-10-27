"""Cliente Groq com timeout, identificação e tentativas limitadas."""

import json
import time
import urllib.error
import urllib.request


def completion(payload, key):
    request = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "User-Agent": "termo-devops/1.0",
        },
    )
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                raw = json.load(response)
            return json.loads(raw["choices"][0]["message"]["content"])
        except urllib.error.HTTPError as error:
            if error.code not in {429, 500, 502, 503, 504} or attempt == 2:
                raise
            delay = min(10, max(1, float(error.headers.get("Retry-After", 2 ** (attempt + 1)))))
            time.sleep(delay)
    raise RuntimeError("API sem resposta")
