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

All config lives in `.env` at the project root — change values in one place:

```env
BASE_URL=http://192.168.1.5:8080
LLM_URL=http://192.168.1.5:8080/v1/chat/completions
MODEL=gemma
WEATHER_API_KEY=your_key_here
```

`config.py` loads it automatically via `python-dotenv`:

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
| [`.env`](./.env) | Environment config — URL, model, API keys |
| [`config.py`](./config.py) | Loads `.env` — single import for all examples |
| [`01_roles.py`](./01_roles.py) | `system`, `user`, `assistant` roles |
| [`02_temperature.py`](./02_temperature.py) | `temperature` from 0 to 1.2 |
| [`03_multi_turn.py`](./03_multi_turn.py) | Multi-turn conversation with history |
| [`04_tokens_and_content.py`](./04_tokens_and_content.py) | `max_tokens`, `stop`, token usage |
| [`05_structured_output.py`](./05_structured_output.py) | Forcing JSON output reliably |
| [`06_streaming.py`](./06_streaming.py) | `stream: True` with SSE parsing |

---

## Tools

The `Tools/` folder is a fully working AI tool-calling agent. The LLM decides which tool to use, Python executes it, and the result is fed back for a final answer.

```
User prompt → LLM picks tool → Python runs it → LLM answers
```

### Run a query

```bash
cd Tools
python ai_tool_agent.py -p "What is the current weather in Jaipur?"
python ai_tool_agent.py -p "What is Tesla stock price today?"
python ai_tool_agent.py -p "What is 128 multiplied by 4?"
python ai_tool_agent.py -p "Save a file called notes.txt with content: Hello World"
```

### Test all tools

```bash
python test_tools.py
```

### Available tools

| File | Functions | Description |
|---|---|---|
| `tool_calculator.py` | `add`, `subtract`, `multiply`, `divide` | Basic math |
| `tool_stock.py` | `get_stock_price(symbol)` | Latest stock price via yfinance |
| `tool_weather.py` | `get_weather(city)` | Current weather via OpenWeatherMap |
| `tool_file_writer.py` | `save_text_file(filename, content)` | Saves text to `generated_files/` |

### Adding a new tool

Create `Tools/tool_<name>.py` with a function and a docstring — auto-registered:

```python
def my_tool(param: str) -> dict:
    """Does something useful"""
    ...
```

### Logging

Every run writes to `Tools/logs/`:

| File | Content |
|---|---|
| `tools.log` | Warnings and errors |
| `flow.log` | Full step-by-step execution trace |

→ See [`Tools/How to use tools.md`](./Tools/How%20to%20use%20tools.md) for full details

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
