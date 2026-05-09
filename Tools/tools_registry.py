import importlib
import inspect
import glob
import os
from logger import get_logger, log_section, flow

log = get_logger(__name__)

# Each entry: { "fn": callable, "description": str, "args": [str] }
REGISTRY: dict = {}

def _load_tools():
    tools_dir = os.path.dirname(__file__)
    pattern   = os.path.join(tools_dir, "tool_*.py")
    files     = sorted(glob.glob(pattern))

    log_section("tool discovery")
    flow("Scanning pattern: %s", pattern)
    flow("Files found: %d → %s", len(files), [os.path.basename(f) for f in files])

    for filepath in files:
        module_name = os.path.splitext(os.path.basename(filepath))[0]
        flow("Loading module: %s", module_name)

        try:
            spec = importlib.util.spec_from_file_location(module_name, filepath)
            mod  = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
        except Exception as e:
            log.error("Failed to load tool module %s: %s", module_name, e, exc_info=True)
            flow("LOAD ERROR: %s → %s", module_name, e)
            continue

        registered = []
        for name, fn in inspect.getmembers(mod, inspect.isfunction):
            if fn.__module__ != module_name:
                continue
            params = list(inspect.signature(fn).parameters.keys())
            doc    = (fn.__doc__ or name.replace("_", " ")).strip()
            REGISTRY[name] = {"fn": fn, "args": params, "description": doc}
            registered.append(f"{name}({', '.join(params)})")

        flow("  Registered from %s: %s", module_name, registered if registered else "none")

    flow("REGISTRY READY: %d tools → %s", len(REGISTRY), list(REGISTRY.keys()))

_load_tools()


def build_system_prompt() -> str:
    flow("Building system prompt from %d registered tools", len(REGISTRY))
    lines = ["You are an AI assistant with access to tools.", "",
             "Available tools:", ""]
    for i, (name, meta) in enumerate(REGISTRY.items(), 1):
        args_str = ", ".join(meta["args"])
        lines.append(f"{i}. {name}({args_str}) — {meta['description']}")
    lines += [
        "",
        "If a tool is needed, respond ONLY with valid JSON:",
        "",
        '{ "tool": "tool_name", "args": { "arg1": value } }',
        "",
        "Otherwise respond normally.",
    ]
    prompt = "\n".join(lines)
    flow("System prompt built (%d chars)", len(prompt))
    return prompt


def call_tool(name: str, args: dict):
    if name not in REGISTRY:
        log.error("Unknown tool requested: %s | available: %s", name, list(REGISTRY.keys()))
        flow("UNKNOWN TOOL: %s", name)
        raise ValueError(f"Unknown tool: {name}")

    flow("DISPATCH → %s | args=%s", name, args)
    result = REGISTRY[name]["fn"](**args)
    flow("DISPATCH ← %s | result=%s", name, result)
    return result
