# Setting Up llama.cpp on Windows

> ← Back to [README](./README.md) | Next: [Run the Server](./run_local_llm_cpp.md)

---

## Step 1 — Download llama.cpp

Go to the [llama.cpp releases page](https://github.com/ggerganov/llama.cpp/releases) and download:

| Your hardware | File to download |
|---------------|-----------------|
| CPU only | `llama-bXXXX-bin-win-cpu-x64.zip` |
| NVIDIA GPU | `llama-bXXXX-bin-win-cuda-cu12-x64.zip` |

Extract to a folder, e.g. `C:\llama.cpp\`

---

## Step 2 — Get a Model (GGUF format)

Download a `.gguf` model from [Hugging Face](https://huggingface.co/models?library=gguf), e.g.:

- `gemma-2b-it.Q4_K_M.gguf`
- `mistral-7b-instruct-v0.2.Q3_K_M.gguf`

Place it in `C:\llama.cpp\models\`

---

## Step 3 — Start the Server

```powershell
cd C:\llama.cpp

.\llama-server.exe `
  -m models\gemma-2b-it.Q4_K_M.gguf `
  -c 4096 `
  -t 8 `
  --host 0.0.0.0 `
  --port 8080
```

> Use `--host 0.0.0.0` to expose on your LAN. Access locally at `http://localhost:8080`.

---

## Step 4 — Verify

Open in browser: `http://localhost:8080` — you should see the built-in chat UI.

Or run a quick health check:
```bash
curl http://localhost:8080/health
```

---

## GUI Options

| Option | Best for |
|--------|----------|
| llama.cpp built-in (`http://localhost:8080`) | Minimal, no extra install |
| [LM Studio](https://lmstudio.ai) | Quick polished UI, zero setup |
| [Open WebUI](https://github.com/open-webui/open-webui) + Docker | Chat history, RAG, multi-model |

### Open WebUI with Docker
```powershell
docker run -d `
  -p 3000:8080 `
  -e OPENAI_API_BASE_URL=http://localhost:8080/v1 `
  -e OPENAI_API_KEY=none `
  --name open-webui `
  ghcr.io/open-webui/open-webui:main
```
Then open `http://localhost:3000`.

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Using `.bin` models | Use `.gguf` format only |
| Forgetting `-c` | Always set context size, e.g. `-c 4096` |
| Mixing CUDA and CPU builds | Use one build consistently |
| Multiple instances on same port | Kill existing process before restarting |

---

Once the server is running, go to [Run the Server](./run_local_llm_cpp.md) for API usage, curl examples, and Node.js setup.
