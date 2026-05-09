import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import requests
import json
import time
from config import LLM_URL, MODEL
from tools_registry import build_system_prompt, call_tool
from logger import get_logger, log_section, flow

log = get_logger(__name__)


def ask_llm(messages: list) -> tuple[str, dict]:
    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": 0,
    }

    flow("→ LLM REQUEST | model=%s | messages=%d", MODEL, len(messages))
    flow("  payload: %s", json.dumps(payload, indent=2))

    start = time.perf_counter()
    response = requests.post(LLM_URL, json=payload)
    elapsed = time.perf_counter() - start

    response.raise_for_status()
    data = response.json()

    reply   = data["choices"][0]["message"]["content"]
    usage   = data.get("usage", {})
    finish  = data["choices"][0].get("finish_reason", "unknown")

    flow("← LLM RESPONSE | elapsed=%.2fs | finish_reason=%s", elapsed, finish)
    flow("  usage: prompt_tokens=%s | completion_tokens=%s | total=%s",
         usage.get("prompt_tokens"), usage.get("completion_tokens"), usage.get("total_tokens"))
    flow("  reply: %s", reply)

    return reply, usage


def run_agent(user_prompt: str):
    log_section(f"agent session start")
    flow("USER PROMPT: %s", user_prompt)

    system_prompt = build_system_prompt()
    flow("SYSTEM PROMPT:\n%s", system_prompt)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": user_prompt},
    ]

    print(f"\n🧠 User: {user_prompt}")
    iteration = 0

    while True:
        iteration += 1
        log_section(f"loop iteration {iteration}")
        flow("MESSAGES IN CONTEXT: %d", len(messages))

        reply, usage = ask_llm(messages)

        try:
            tool_call = json.loads(reply)
            tool_name = tool_call["tool"]
            args      = tool_call.get("args", {})

            flow("TOOL DECISION: LLM chose tool=%s | args=%s", tool_name, args)
            print(f"\n🔧 Calling tool: {tool_name}({args})")

            result = call_tool(tool_name, args)

            flow("TOOL RESULT: %s", result)
            print(f"✅ Result: {result}")

            messages.append({"role": "assistant", "content": reply})
            messages.append({"role": "user",      "content": f"Tool result: {json.dumps(result)}"})
            flow("CONTEXT UPDATED: feeding result back to LLM")

        except json.JSONDecodeError:
            flow("NO TOOL CALL: LLM replied with plain text → final answer")
            flow("FINAL ANSWER: %s", reply)
            log_section("session end")
            print(f"\n💬 Assistant: {reply}")
            break

        except KeyError as e:
            log.warning("Malformed tool JSON — missing key: %s | reply: %s", e, reply)
            flow("MALFORMED TOOL JSON: missing key=%s | raw=%s", e, reply)
            break

        except Exception as e:
            log.error("Tool execution failed: %s", e, exc_info=True)
            flow("ERROR during tool execution: %s", e)
            break


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="AI Tool Agent")
    parser.add_argument("-p", "--prompt", type=str, required=True, help="Your query for the agent")
    args = parser.parse_args()

    run_agent(args.prompt)
