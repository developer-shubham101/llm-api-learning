"""
06_streaming.py — Streaming Responses

By default, the API waits until the full response is ready, then sends it.
With `stream: True`, the model sends tokens as they are generated (like ChatGPT typing).

Why use streaming?
- Better UX: user sees output immediately instead of waiting
- Useful for long responses (stories, code, reports)

The response comes as Server-Sent Events (SSE):
  data: {"choices":[{"delta":{"content":"Hello"}}]}
  data: {"choices":[{"delta":{"content":" world"}}]}
  data: [DONE]
"""

import requests
import json
import sys
from config import LLM_URL, MODEL

def stream_chat(user_message):
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": user_message}],
        "temperature": 0.7,
        "stream": True,   # ← enable streaming
    }

    # Use stream=True in requests.post
    response = requests.post(LLM_URL, json=payload, stream=True)
    response.raise_for_status()

    sys.stdout.write("AI: ")
    sys.stdout.flush()

    full_text = ""

    # Iterate over the response lines
    for line in response.iter_lines():
        if line:
            decoded_line = line.decode('utf-8')
            if decoded_line.startswith("data: "):
                payload_str = decoded_line[6:].strip()
                
                if payload_str == "[DONE]":
                    break
                
                try:
                    data = json.loads(payload_str)
                    token = data["choices"][0].get("delta", {}).get("content", "")
                    sys.stdout.write(token)
                    sys.stdout.flush()
                    full_text += token
                except json.JSONDecodeError:
                    continue

    print("\n\n[Stream complete]")
    print(f"Full text length: {len(full_text)} chars")
    return full_text

def main():
    print("=== Streaming a long response ===\n")
    stream_chat("Write a short poem about the ocean. Make it 4 stanzas.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nError: {e}")
