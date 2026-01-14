# Implementation Guide

**Date:** January 2026

This guide provides step-by-step instructions to populate the scaffolding with logic.

## 1. Environment Setup

### Why `venv` for Development?
While we ship in Docker, we develop in `venv` because Docker file-syncing and rebuilding layers adds latency. We use `poetry` to ensure the `pyproject.toml` stays the source of truth for both environments.

**Commands:**
1. Install Poetry (if not installed).
2. `poetry install`: Creates the venv and installs deps.
3. `cp .env.example .env`: specific your `GOOGLE_API_KEY`.

## 2. Implementing Logic (Step-by-Step)

### Step A: Configuration (`src/config.py`)
**Task**: Use Pydantic Settings to validate the `.env`.
**Why Pydantic?** It fails *fast*. If `GOOGLE_API_KEY` is missing, the app crashes immediately on startup with a clear error, rather than failing randomly deep in an API call.

### Step B: The LLM Wrapper (`src/core/llm.py`)
**Task**: Implement `get_llm()`.
**Code Snippet Idea**:
```python
from langchain_google_genai import ChatGoogleGenerativeAI
from src.config import settings

def get_llm():
    return ChatGoogleGenerativeAI(
        model=settings.gemini_model,
        google_api_key=settings.google_api_key.get_secret_value(),
        temperature=0
    )
```
**Note**: Gemini 2.5/3 models are multimodal by default. Ensure your `langchain-google-genai` package is up to date.

### Step C: Define State (`src/core/state.py`)
**Task**: Define what data persists.
Use `langgraph.graph.MessagesState` or a custom `TypedDict`.
```python
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
import operator

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]
```
**Why `operator.add`?** This tells LangGraph that when a node returns new messages, they should be *appended* to the list, not overwrite them.

### Step D: Build Tools (`src/tools/filesystem.py`)
**Task**: Implement `write_file` and `read_file` functions decorated with `@tool`.
**Crucial Security**: Always validate that the path starts with `settings.workspace_root`. Do not allow  traversal.

### Step E: The Graph (`src/agent/graph.py`)
**Task**: Stitch it together.
1. Initialize `StateGraph(AgentState)`.
2. Add nodes: `builder.add_node("reason", reason_node)`.
3. Add edges:
   - From `start` to `reason`.
   - From `reason` conditional edge:
     - If tool calls present -> `tools`.
     - If final answer -> `end`.

## 3. Running & Verifying

### Run Locally
```bash
poetry run python -m src.main
```

### Run in Docker
```bash
docker-compose up --build
```
This serves as the ultimate integration test. If it works here, it works in production.
