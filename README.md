# LLM API Learning Project

A hands-on Python project to learn every key concept of the LLM Chat Completions API using a local model (Gemma via llama.cpp).

> Need to set up or run the local LLM server first?
> - [Setup llama.cpp](./setup_llm_cpp.md) — install and configure llama.cpp
> - [Run llama.cpp server](./run_local_llm_cpp.md) — start the server and test it

---

## Setup

```bash
pip install -r requirements.txt
```

Run any example:
```bash
python 01_roles.py
python 02_temperature.py
# etc.
```

---

## Configuration

All examples share a single config file — **change the URL or model in one place**:

```python
# config.py
BASE_URL = "http://localhost:8080"
LLM_URL  = f"{BASE_URL}/v1/chat/completions"
MODEL    = "gemma"
```

Every example imports from it:
```python
from config import LLM_URL, MODEL
```

---

## Core Concepts

### `messages` — The Conversation Array

Every request sends a `messages` array. Each message has two fields:

| Field     | Description                                             |
|-----------|---------------------------------------------------------|
| `role`    | Who is speaking: `system`, `user`, or `assistant`       |
| `content` | The actual text of the message                          |

```python
messages=[
    {"role": "system",    "content": "You are a helpful assistant."},
    {"role": "user",      "content": "What is 2 + 2?"},
    {"role": "assistant", "content": "It is 4."},   # prior AI turn
    {"role": "user",      "content": "Multiply that by 3."},
]
```

---

### Roles Explained

| Role        | Purpose |
|-------------|---------|
| `system`    | Sets the AI's behavior, persona, or constraints. Processed first. |
| `user`      | The human's input or question. |
| `assistant` | A previous AI reply. Used to build conversation history. |

→ See [`01_roles.py`](./01_roles.py)

---

### `temperature` — Creativity Dial

Controls how random/creative the output is.

| Value  | Behavior |
|--------|----------|
| `0.0`  | Deterministic — always picks the most likely token. Best for code, facts. |
| `0.5`  | Balanced — good general-purpose default. |
| `1.0+` | Very creative/random — good for stories, brainstorming. |

```python
{"temperature": 0.0}  # predictable
{"temperature": 1.2}  # creative
```

→ See [`02_temperature.py`](./02_temperature.py)

---

### Multi-Turn Conversations

LLMs are **stateless** — they don't remember previous requests. To simulate memory, append every message and reply to the `messages` list and resend the full history each time.

```python
history.append({"role": "user",      "content": user_message})
# ... get reply ...
history.append({"role": "assistant", "content": reply})
```

→ See [`03_multi_turn.py`](./03_multi_turn.py)

---

### `max_tokens` — Output Length Limit

Hard cap on how many tokens the model can generate in its reply.

- 1 token ≈ 0.75 words
- If the model hits the limit, `finish_reason` will be `"length"` instead of `"stop"`

```python
{"max_tokens": 100}
```

### `stop` — Stop Sequences

Stops generation as soon as the model produces one of the given strings.

```python
{"stop": ["3.", "\n\n"]}
```

### Token Usage

Every response includes a `usage` object:

```json
{
  "prompt_tokens": 42,
  "completion_tokens": 18,
  "total_tokens": 60
}
```

→ See [`04_tokens_and_content.py`](./04_tokens_and_content.py)

---

### Structured / JSON Output

LLMs output plain text by default. Three strategies to get reliable JSON:

1. System prompt: `"You output ONLY valid JSON. No markdown."`
2. Schema hint: pass the expected shape in the user prompt
3. Clean output: strip markdown fences before `json.loads()`

→ See [`05_structured_output.py`](./05_structured_output.py)

---

### `stream` — Streaming Responses

With `stream: True`, tokens arrive as Server-Sent Events (SSE) as they are generated.

```python
{"stream": True}
```

Response chunks:
```
data: {"choices":[{"delta":{"content":"Hello"}}]}
data: {"choices":[{"delta":{"content":" world"}}]}
data: [DONE]
```

→ See [`06_streaming.py`](./06_streaming.py)

---

### `finish_reason` — Why the Model Stopped

| Value      | Meaning |
|------------|---------|
| `"stop"`   | Model naturally finished its response |
| `"length"` | Hit `max_tokens` limit — response may be incomplete |

---

## Files

| File | Concept |
|------|---------|
| [`config.py`](./config.py) | Central config — base URL, model name |
| [`01_roles.py`](./01_roles.py) | `system`, `user`, `assistant` roles |
| [`02_temperature.py`](./02_temperature.py) | `temperature` from 0 to 1.2 |
| [`03_multi_turn.py`](./03_multi_turn.py) | Multi-turn conversation with history |
| [`04_tokens_and_content.py`](./04_tokens_and_content.py) | `max_tokens`, `stop`, token usage |
| [`05_structured_output.py`](./05_structured_output.py) | Forcing JSON output reliably |
| [`06_streaming.py`](./06_streaming.py) | `stream: True` with SSE parsing |

---

## Full Request Reference

```python
import requests
from config import LLM_URL, MODEL

requests.post(LLM_URL, json={
    "model":       MODEL,
    "messages":    [...],      # conversation history
    "temperature": 0.7,        # creativity (0.0 – 2.0)
    "max_tokens":  512,        # max output tokens
    "stop":        ["END"],    # stop sequences
    "stream":      False,      # True = stream tokens as SSE
})
```
