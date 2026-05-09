# How To Use Tools

In this project, a "tool" is a Python function the LLM can call to do real work.

```
User prompt
    ↓
LLM decides which tool to use → responds with JSON
    ↓
Python executes the tool function
    ↓
Result fed back to LLM → final natural language answer
```

---

## Architecture

```
Tools/
├── ai_tool_agent.py      ← CLI entry point — runs the agent loop
├── tools_registry.py     ← auto-discovers all tool_*.py files
├── logger.py             ← shared logger (console + file + flow trace)
├── test_tools.py         ← test script — runs a sample query per tool
├── tool_calculator.py    ← add, subtract, multiply, divide
├── tool_stock.py         ← get_stock_price
├── tool_weather.py       ← get_weather
└── tool_file_writer.py   ← save_text_file
```

---

## Running the Agent

Pass your query with `-p` or `--prompt`:

```bash
cd Tools
python ai_tool_agent.py -p "What is the current weather in Jaipur?"
python ai_tool_agent.py -p "What is Tesla stock price today?"
python ai_tool_agent.py -p "What is 128 multiplied by 4?"
python ai_tool_agent.py -p "Save a file called notes.txt with content: Hello World"
```

Running without `-p` prints usage:

```
usage: ai_tool_agent.py [-h] -p PROMPT
ai_tool_agent.py: error: the following arguments are required: -p/--prompt
```

---

## Testing All Tools

Run the test script to fire a sample query through every registered tool:

```bash
cd Tools
python test_tools.py
```

Output:

```
============================================================
  TOOL TEST SCRIPT — 7 tests
============================================================

[1/7] Testing tool: add
  Query: What is 128 plus 256?
------------------------------------------------------------
🧠 User: What is 128 plus 256?
🔧 Calling tool: add({'a': 128, 'b': 256})
✅ Result: 384
💬 Assistant: 128 plus 256 equals 384.

...

============================================================
  RESULTS: 7/7 passed
  ✅ All tests passed
============================================================
```

---

## Logging

Two log files are written to `Tools/logs/` on every run:

| File | Content |
|---|---|
| `tools.log` | Warnings and errors only |
| `flow.log` | Full execution trace — every step of the flow |

Console only shows warnings and errors to stay clean.

Sample `flow.log` trace:

```
============================================================
  AGENT SESSION START
============================================================
USER PROMPT: What is the current weather in Jaipur?
SYSTEM PROMPT: ...

============================================================
  TOOL DISCOVERY
============================================================
Files found: 4 → ['tool_calculator.py', 'tool_file_writer.py', ...]
REGISTRY READY: 7 tools → ['add', 'subtract', 'multiply', ...]

============================================================
  LOOP ITERATION 1
============================================================
→ LLM REQUEST | model=gemma | messages=2
← LLM RESPONSE | elapsed=1.43s | finish_reason=stop
  usage: prompt_tokens=91 | completion_tokens=24 | total=115
  reply: {"tool": "get_weather", "args": {"city": "Jaipur"}}
TOOL DECISION: LLM chose tool=get_weather | args={'city': 'Jaipur'}
DISPATCH → get_weather | args={'city': 'Jaipur'}
DISPATCH ← get_weather | result={'city': 'Jaipur', 'temperature': 34.2, ...}
CONTEXT UPDATED: feeding result back to LLM

============================================================
  LOOP ITERATION 2
============================================================
FINAL ANSWER: The current weather in Jaipur is 34.2°C with clear sky.

============================================================
  SESSION END
============================================================
```

---

## Configuration

All config lives in `.env` at the project root:

```env
BASE_URL=http://192.168.1.5:8080
LLM_URL=http://192.168.1.5:8080/v1/chat/completions
MODEL=gemma
WEATHER_API_KEY=your_key_here
```

`config.py` loads it automatically — no hardcoded values anywhere.

---

## Adding a New Tool

1. Create `tool_<name>.py` in the `Tools/` folder
2. Write a function with a docstring

```python
# tool_translator.py

def translate_text(text: str, target_language: str) -> dict:
    """Translate text into a target language"""
    return {"translated": "..."}
```

The registry picks it up automatically — no other files need to change.

---

## Available Tools

| File | Functions | Description |
|---|---|---|
| `tool_calculator.py` | `add`, `subtract`, `multiply`, `divide` | Basic math |
| `tool_stock.py` | `get_stock_price(symbol)` | Latest stock price via yfinance |
| `tool_weather.py` | `get_weather(city)` | Current weather via OpenWeatherMap |
| `tool_file_writer.py` | `save_text_file(filename, content)` | Saves text to `generated_files/` |

> `tool_weather.py` requires a real API key — set `WEATHER_API_KEY` in `.env`.

---

## How the Agent Loop Works

```
1. Build system prompt dynamically from registry
2. Send user prompt + system prompt to LLM
3. If LLM replies with JSON  → execute tool → feed result back → repeat
4. If LLM replies with text  → print final answer → stop
```

Supports tool chaining — the LLM can call multiple tools before giving a final answer.

---

## Key Concepts

| Concept | Where |
|---|---|
| CLI entry point | `ai_tool_agent.py` → `argparse` `-p` flag |
| Auto-discovery | `tools_registry.py` → `_load_tools()` |
| Dynamic system prompt | `tools_registry.py` → `build_system_prompt()` |
| Tool dispatch | `tools_registry.py` → `call_tool()` |
| Agent loop + chaining | `ai_tool_agent.py` → `run_agent()` |
| Flow logging | `logger.py` → `flow()` + `log_section()` |
| Tool testing | `test_tools.py` → `run_tests()` |
