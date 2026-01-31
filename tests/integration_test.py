import asyncio
import sys
import os

# Add project root to sys.path to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.agent.graph import app
from src.core.state import AgentState


async def test_agent_graph():
    print("Starting Integration Test for Agent Zero Graph...")

    # Test 1: Simple Reasoning & File Writing
    print("\n--- Test 1: Reasoning & File Writing ---")
    initial_state = {
        "messages": [
            (
                "user",
                "Write a file named 'test_check.txt' containing 'INTEGRATION_TEST_PASSED'",
            )
        ],
        "step_count": 0,
    }

    found_success = False
    async for event in app.astream(initial_state):
        for key, value in event.items():
            print(f"Node: {key}")
            last_msg = value["messages"][-1]
            if hasattr(last_msg, "content") and "INTEGRATION_TEST_PASSED" in str(
                last_msg.content
            ):
                found_success = True
            if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
                for tc in last_msg.tool_calls:
                    print(f"  Tool Call: {tc['name']}")

    # Verify file existence
    from src.config import settings

    test_file = os.path.join(settings.workspace_root, "test_check.txt")
    if os.path.exists(test_file):
        with open(test_file, "r") as f:
            content = f.read()
            if "INTEGRATION_TEST_PASSED" in content:
                print("[PASS] Test 1: File created with correct content.")
            else:
                print("[FAIL] Test 1: Content mismatch.")
    else:
        print("[FAIL] Test 1: File not found.")

    # Test 2: Web Search
    print("\n--- Test 2: Web Search (DuckDuckGo) ---")
    initial_state = {
        "messages": [("user", "Search for the current weather in Tokyo and tell me.")],
        "step_count": 0,
    }

    search_called = False
    async for event in app.astream(initial_state):
        for key, value in event.items():
            last_msg = value["messages"][-1]
            if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
                for tc in last_msg.tool_calls:
                    if tc["name"] == "search_web":
                        search_called = True
                        print("  Tool Call: search_web detected.")

    if search_called:
        print("[PASS] Test 2: Agent attempted to use web search.")
    else:
        print("[FAIL] Test 2: search_web tool not invoked.")


if __name__ == "__main__":
    asyncio.run(test_agent_graph())
