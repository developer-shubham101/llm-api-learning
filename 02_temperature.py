"""
02_temperature.py — Understanding Temperature

`temperature` controls how creative/random the model's output is.

 0.0  → Deterministic, always picks the most likely word (best for facts/code)
 0.5  → Balanced (good for general use)
 1.0+ → Very creative/random (good for stories, brainstorming)

Think of it like a "creativity dial".
"""

import requests
from config import LLM_URL, MODEL

def ask(prompt, temperature):
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "user", "content": prompt},
        ],
        "temperature": temperature,
    }
    response = requests.post(LLM_URL, json=payload)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"].strip()

def main():
    prompt = "Write a one-sentence tagline for a coffee shop."

    # Run the same prompt 3 times at different temperatures
    for temp in [0.0, 0.5, 1.2]:
        print(f"\n=== temperature: {temp} ===")
        # Run twice to show consistency vs randomness
        print("Run 1:", ask(prompt, temp))
        print("Run 2:", ask(prompt, temp))

    # ── Practical use-case: low temp for code ────────────────────────────────
    print("\n=== Low temp (0.1) for code generation ===")
    code = ask("Write a JS function that adds two numbers.", 0.1)
    print(code)

    # ── Practical use-case: high temp for story ──────────────────────────────
    print("\n=== High temp (1.1) for creative story ===")
    story = ask("Start a story about a robot who discovers music.", 1.1)
    print(story)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
