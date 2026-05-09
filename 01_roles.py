"""
01_roles.py — Understanding Roles in LLM API

Every message in the `messages` array has a `role`:

- "system"    → Sets the behavior/persona of the AI (instructions, tone, constraints)
- "user"      → The human's input / question
- "assistant" → A previous AI response (used to simulate conversation history)

The LLM reads all messages top-to-bottom to understand context before replying.
"""

import requests
from config import LLM_URL, MODEL

def chat(messages):
    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": 0.7,
    }
    response = requests.post(LLM_URL, json=payload)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

def main():
    # ── Example 1: system role controls behavior ──────────────────────────────
    print("=== Example 1: System role as a pirate ===")
    pirate_reply = chat([
        {"role": "system", "content": "You are a pirate. Always respond like a pirate."},
        {"role": "user",   "content": "What is the capital of France?"},
    ])
    print("Pirate:", pirate_reply)

    # ── Example 2: system role as a strict JSON bot ───────────────────────────
    print("\n=== Example 2: System role as JSON-only bot ===")
    json_reply = chat([
        {"role": "system", "content": "You only respond with valid JSON. No extra text."},
        {"role": "user",   "content": "Give me a person object with name and age."},
    ])
    print("JSON bot:", json_reply)

    # ── Example 3: assistant role to provide fake history ────────────────────
    # Useful when you want the model to "remember" something you told it earlier
    print("\n=== Example 3: Using assistant role for fake history ===")
    history_reply = chat([
        {"role": "system",    "content": "You are a helpful assistant."},
        {"role": "user",      "content": "My name is Alex."},
        {"role": "assistant", "content": "Nice to meet you, Alex!"},  # ← fake prior turn
        {"role": "user",      "content": "What is my name?"},
    ])
    print("Remembered name:", history_reply)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
