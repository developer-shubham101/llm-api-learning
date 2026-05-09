"""
03_multi_turn.py — Multi-Turn Conversations

LLMs are stateless — they don't remember previous requests.
To simulate memory, you must send the FULL conversation history
in every request by appending each new message to the `messages` array.

Pattern:
  1. User sends message → push to history
  2. Get AI reply       → push to history
  3. Repeat
"""

import requests
import json
from config import LLM_URL, MODEL

# Conversation history — grows with each turn
history = [
    {"role": "system", "content": "You are a helpful math tutor. Be concise."},
]

def chat(user_message):
    # 1. Add user message to history
    history.append({"role": "user", "content": user_message})

    payload = {
        "model": MODEL,
        "messages": history,   # ← send full history every time
        "temperature": 0.3,
    }
    
    response = requests.post(LLM_URL, json=payload)
    response.raise_for_status()
    
    reply = response.json()["choices"][0]["message"]["content"].strip()

    # 2. Add assistant reply to history so next turn remembers it
    history.append({"role": "assistant", "content": reply})

    return reply

def main():
    # Simulated 3-turn conversation
    turns = [
        "What is the Pythagorean theorem?",
        "Can you give me a simple example with numbers?",
        "Now explain why a² + b² = c² in plain English.",
    ]

    for turn in turns:
        print(f"\nUser: {turn}")
        reply = chat(turn)
        print(f"AI:   {reply}")

    # Show the full history that was built up
    print("\n=== Full conversation history sent in last request ===")
    print(json.dumps(history, indent=2))

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
