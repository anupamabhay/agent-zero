import json
import os
from langchain_core.tools import tool
from src.config import settings

MEMORY_FILE = "agent_memory.json"


def _get_memory_path():
    return os.path.join(settings.workspace_root, MEMORY_FILE)


def _load_memory():
    path = _get_memory_path()
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}


def _save_memory(memory):
    path = _get_memory_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=4)


@tool
def store_fact(key: str, value: str) -> str:
    """Stores a fact or preference in the agent's long-term memory."""
    memory = _load_memory()
    memory[key] = value
    _save_memory(memory)
    return f"Stored fact: {key} = {value}"


@tool
def retrieve_fact(key: str) -> str:
    """Retrieves a fact or preference from the agent's long-term memory."""
    memory = _load_memory()
    if key in memory:
        return f"Fact for '{key}': {memory[key]}"
    return f"No fact found for '{key}'."


@tool
def list_all_facts() -> str:
    """Lists all facts stored in the agent's long-term memory."""
    memory = _load_memory()
    if not memory:
        return "Memory is empty."

    facts = [f"{k}: {v}" for k, v in memory.items()]
    return "Stored facts:\n" + "\n".join(facts)
