# llm_interface.py

import requests
import json
import time
from config import OPENROUTER_API_KEY, LLM_MODEL

# Full-blocking LLM call (for debugging or fallback)
def call_llm(prompt, system="You are a conscious AI."):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.8
    }

    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"].strip()

# ✅ Streaming LLM response using OpenRouter

def call_llm_stream(prompt, system="You are a conscious AI."):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": LLM_MODEL,
        "stream": True,
        "temperature": 0.8,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ]
    }

    retry_count = 0
    max_retries = 5
    base_wait = 5  # Start with 5 seconds

    while retry_count < max_retries:
        try:
            with requests.post(url, headers=headers, json=data, stream=True) as r:
                if r.status_code == 429:
                    retry_count += 1
                    wait = base_wait * (2 ** (retry_count - 1))  # 5, 10, 20, 40, 80 seconds
                    print(f"\n⚠️ Rate limit hit. Retrying in {wait}s... (attempt {retry_count}/{max_retries})")
                    print(f"💡 Tip: Consider using a different model or waiting a bit between requests.")
                    time.sleep(wait)
                    continue
                elif r.status_code == 402:
                    print("\n❌ Payment required. Please check your OpenRouter credits.")
                    raise Exception("Insufficient credits on OpenRouter")
                elif r.status_code == 401:
                    print("\n❌ Authentication failed. Please check your OPENROUTER_API_KEY.")
                    raise Exception("Invalid API key")

                r.raise_for_status()

                for line in r.iter_lines():
                    if line and line.startswith(b'data: '):
                        raw = line[len(b'data: '):].decode('utf-8')
                        if raw.strip() == "[DONE]":
                            break
                        try:
                            content = json.loads(raw)["choices"][0]["delta"].get("content", "")
                            if content:
                                yield content
                        except Exception:
                            continue
                return  # Success - exit the function
                
        except requests.exceptions.ConnectionError:
            print(f"\n❌ Connection error. Please check your internet connection.")
            raise
        except requests.exceptions.RequestException as e:
            if "429" not in str(e):  # Don't double-log rate limit errors
                print(f"\n❌ OpenRouter error: {e}")
            retry_count += 1
            if retry_count >= max_retries:
                raise Exception(f"Failed after {max_retries} retries: {e}")
            wait = base_wait * (2 ** (retry_count - 1))
            print(f"Retrying in {wait}s...")
            time.sleep(wait)
    
    # If we get here, all retries were exhausted
    raise Exception(f"Rate limit persists after {max_retries} retries. Please try again later or switch models.")