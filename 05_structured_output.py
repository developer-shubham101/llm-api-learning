"""
05_structured_output.py — Forcing Structured / JSON Output

LLMs output plain text by default. To get reliable structured data:

Strategy 1: System prompt instruction  → tell it to ONLY output JSON
Strategy 2: Provide a JSON schema      → show the exact shape you want
Strategy 3: Clean + parse the output   → strip markdown fences, then json.loads()

This is critical for building apps that consume LLM output programmatically.
"""

import requests
import json
import re
from config import LLM_URL, MODEL

def clean_json(raw):
    # Strip markdown code fences that local LLMs often add
    return re.sub(r"```json|```", "", raw).strip()

def ask_json(user_prompt):
    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                # Strategy 1: explicit instruction in system prompt
                "content": "You output ONLY valid JSON. No explanation. No markdown. No extra text.",
            },
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.2, # low temp = more predictable structure
    }
    
    response = requests.post(LLM_URL, json=payload)
    response.raise_for_status()
    
    raw = response.json()["choices"][0]["message"]["content"]
    cleaned = clean_json(raw)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        print("Failed to parse JSON. Raw output:\n", raw)
        return None

def main():
    # ── Example 1: Simple object ──────────────────────────────────────────────
    print("=== Example 1: Simple object ===")
    person = ask_json(
        'Return a JSON object with fields: name (string), age (number), city (string).'
    )
    print(person)

    # ── Example 2: Array of objects ───────────────────────────────────────────
    print("\n=== Example 2: Array of objects ===")
    products = ask_json(
        'Return a JSON array of 3 products. Each product has: id, name, price (number).'
    )
    print(products)

    # ── Example 3: Schema-guided output ──────────────────────────────────────
    print("\n=== Example 3: Schema-guided output ===")
    schema = {
        "country": "string",
        "capital": "string",
        "population": "number",
        "languages": ["string"],
    }
    country = ask_json(
        f"Return data about France using exactly this JSON shape: {json.dumps(schema)}"
    )
    print(country)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
