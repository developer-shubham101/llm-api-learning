import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ai_tool_agent import run_agent
from logger import log_section, flow

# ============================================================
# SAMPLE QUERY PER TOOL
# ============================================================

TESTS = [
    {
        "tool":  "add",
        "query": "What is 128 plus 256?",
    },
    {
        "tool":  "subtract",
        "query": "What is 500 minus 173?",
    },
    {
        "tool":  "multiply",
        "query": "What is 25 multiplied by 8?",
    },
    {
        "tool":  "divide",
        "query": "What is 144 divided by 12?",
    },
    {
        "tool":  "get_stock_price",
        "query": "What is the current stock price of Apple?",
    },
    {
        "tool":  "get_weather",
        "query": "What is the weather like in London right now?",
    },
    {
        "tool":  "save_text_file",
        "query": "Save a file called test_note.txt with the content: Hello from the tool test script!",
    },
]

# ============================================================
# RUNNER
# ============================================================

def run_tests():
    total  = len(TESTS)
    passed = 0
    failed = []

    print("\n" + "=" * 60)
    print(f"  TOOL TEST SCRIPT — {total} tests")
    print("=" * 60)

    for i, test in enumerate(TESTS, 1):
        tool  = test["tool"]
        query = test["query"]

        print(f"\n[{i}/{total}] Testing tool: {tool}")
        print(f"  Query: {query}")
        print("-" * 60)

        log_section(f"test {i}/{total} — {tool}")
        flow("TEST QUERY: %s", query)

        try:
            run_agent(query)
            passed += 1
            flow("TEST RESULT: PASSED")
        except Exception as e:
            print(f"  ❌ FAILED: {e}")
            flow("TEST RESULT: FAILED — %s", e)
            failed.append({"tool": tool, "error": str(e)})

    # ============================================================
    # SUMMARY
    # ============================================================
    print("\n" + "=" * 60)
    print(f"  RESULTS: {passed}/{total} passed")

    if failed:
        print("\n  Failed tests:")
        for f in failed:
            print(f"  ✗ {f['tool']} → {f['error']}")
    else:
        print("  ✅ All tests passed")

    print("=" * 60)
    flow("FINAL SUMMARY: %d/%d passed | failed=%s", passed, total, [f["tool"] for f in failed])


if __name__ == "__main__":
    run_tests()
