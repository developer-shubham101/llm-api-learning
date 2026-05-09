# Running the llama.cpp Server

> ← Back to [README](./README.md) | [Setup Guide](./setup_llm_cpp.md)

This project connects to a llama.cpp server running at `http://localhost:8080`.

---

## Command Structure

```bash
.\llama-server.exe -m "<MODEL_PATH>" -c <CONTEXT_SIZE> -t <THREADS> --host <HOST> --port <PORT>
```

| Flag | Description |
|------|-------------|
| `-m` | Path to model file (`.gguf` format) |
| `-c` | Context window size (tokens) |
| `-t` | Number of CPU threads |
| `--host` | Host to bind — use `0.0.0.0` to expose on LAN |
| `--port` | Port number |

---

## Start the Server (LAN accessible)

Navigate to your llama.cpp binary directory, then run:

### Gemma Model
```bash
.\llama-server.exe -m "PATH\TO\gemma.gguf" -c 4096 -t 8 --host 0.0.0.0 --port 8080
```

### Mistral 7B Model
```bash
.\llama-server.exe -m "PATH\TO\mistral-7b-instruct-v0.2.Q3_K_M.gguf" -c 4096 -t 8 --host 0.0.0.0 --port 8080
```

> Using `--host 0.0.0.0` makes the server reachable from other devices on your LAN. Access locally at `http://localhost:8080`.

---

## Verify the Server

Once running, test with these curl commands:

### Health check
```bash
curl http://localhost:8080/health
```

### List models
```bash
curl http://localhost:8080/v1/models
```

### Chat completion
```bash
curl -X POST http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemma",
    "messages": [{ "role": "user", "content": "Say hello." }],
    "temperature": 0.7
  }'
```

### Text completion
```bash
curl -X POST http://localhost:8080/completion \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "The future of AI is",
    "n_predict": 50,
    "temperature": 0.8
  }'
```

### Server metrics
```bash
curl http://localhost:8080/metrics
```

---

## Built-in Web UI

Open in browser:
```
http://localhost:8080
```

llama.cpp ships with a built-in chat UI — no extra install needed.

---

## Node.js Setup

This project requires Node.js to run the JavaScript examples.

### Install Node.js

1. Download from [nodejs.org](https://nodejs.org/) (LTS version recommended)
2. Run the installer
3. Verify installation:
   ```bash
   node --version
   npm --version
   ```

### Install Project Dependencies

```bash
cd ai-api
npm install
```

### Run Examples

```bash
node 01_roles.js
node 02_temperature.js
# etc.
```
