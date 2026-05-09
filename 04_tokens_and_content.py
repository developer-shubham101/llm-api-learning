"""
04_tokens_and_content.py — Tokens, max_tokens & Stop Sequences

TOKEN: The basic unit the LLM reads/writes. Roughly 1 token ≈ 0.75 words.

max_tokens  → Hard limit on how many tokens the model can output.
              Useful to control response length and cost.

stop        → Array of strings that tell the model to STOP generating
              as soon as it produces one of them.

content     → The actual text of the message. Can be a plain string
              or (in some APIs) an array of content parts (text + images).
"""

import requests
from config import LLM_URL, MODEL

def ask(payload_extra):
    payload = {"model": MODEL}
    payload.update(payload_extra)
    
    response = requests.post(LLM_URL, json=payload)
    response.raise_for_status()
    
    data = response.json()
    choice = data["choices"][0]
    
    return {
        "content":       choice["message"]["content"].strip(),
        "finish_reason": choice.get("finish_reason"), # "stop" | "length" | "stop_sequence"
        "usage":         data.get("usage"),           # prompt_tokens, completion_tokens, total_tokens
    }

def main():
    # ── Example 1: max_tokens cuts off the response ───────────────────────────
    print("=== max_tokens: 20 (short cut-off) ===")
    short = ask({
        "messages": [{"role": "user", "content": "Explain quantum computing in detail."}],
        "temperature": 0.5,
        "max_tokens": 20,
    })
    print("Content:", short["content"])
    print("Finish reason:", short["finish_reason"]) # "length" means it was cut off
    print("Token usage:", short["usage"])

    # ── Example 2: stop sequence ──────────────────────────────────────────────
    print("\n=== stop sequence: stops at '3.' ===")
    stopped = ask({
        "messages": [{"role": "user", "content": "List 5 planets in our solar system, numbered."}],
        "temperature": 0,
        "stop": ["3."],  # model stops as soon as it writes "3."
    })
    print("Content:", stopped["content"])
    print("Finish reason:", stopped["finish_reason"]) # "stop" from stop sequence

    # ── Example 3: token usage awareness ─────────────────────────────────────
    print("\n=== Token usage for a normal request ===")
    normal = ask({
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user",   "content": "What is 2 + 2?"},
        ],
        "temperature": 0,
    })
    print("Content:", normal["content"])
    print("Tokens used:", normal["usage"])
    # prompt_tokens    = tokens in your messages[]
    # completion_tokens = tokens in the AI reply
    # total_tokens     = sum of both (this is what you're billed for in paid APIs)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
