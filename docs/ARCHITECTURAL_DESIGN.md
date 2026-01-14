# Architectural Design Specification: Production AI Agent

## 1. Executive Summary
This document outlines the architecture for a robust, production-grade AI agent capable of executing tools and manipulating files.
**Core Stack:** Python 3.11+, LangGraph (Orchestration), Google Gemini (Intelligence), Docker (Sandboxing).

## 2. High-Level Design (HLD)

The agent follows a **State Machine Architecture** (ReAct Pattern / Plan-and-Execute) rather than a simple loop.

### 2.1 Component Diagram
```mermaid
graph TD
    User-->|Input Assessment| API[Interface (CLI/API)]
    API -->|Init State| Graph[LangGraph Orchestrator]
    
    subgraph "Agent Runtime (Docker Container)"
        Graph -->|Step 1| Planner[Planning Node]
        Graph -->|Step 2| Executor[Tool Execution Node]
        Graph -->|Step 3| Reflector[Reflection/Critique Node]
        
        Executor -- Uses --> TR[Tool Registry]
        TR -- FileSystem --> FS[File System (Mounted Volume)]
    end
    
    Planner -- API Call --> LLM[Google Gemini Gateway]
    Reflector -- API Call --> LLM
```

### 2.2 Key Decisions
1.  **Orchestrator (LangGraph vs Loops):**
    *   *Decision:* Use LangGraph.
    *   *Reason:* It allows us to define specific "Nodes" (functions) and "Edges" (transition logic). It supports persistence (pausing execution), cycles (retries), and debugging (time-travel) out of the box.
2.  **Runtime (Docker vs Local):**
    *   *Decision:* **Docker**.
    *   *Reason:* Safety. An agent that can write code or delete files should never run directly on the host machine. We will mount a specific `./workspace` folder to the container so the agent can only damage that specific folder, not your entire OS.
3.  **Data Validation (Pydantic):**
    *   *Decision:* All inputs/outputs between nodes must be Pydantic models.
    *   *Reason:* Prevents "stringly typed" programming where the agent crashes because a dictionary key is missing.

## 3. Low-Level Design (LLD)

### 3.1 The State Schema
The core of the agent is the `AgentState`. It tracks the conversation and the "Plan".

```python
from typing import TypedDict, List, Annotated
from langchain_core.messages import BaseMessage
import operator

class AgentState(TypedDict):
    # Append-only list of messages (User inputs, AI thoughts, Tool results)
    messages: Annotated[List[BaseMessage], operator.add]
    # The current structured plan (list of steps)
    plan: List[str]
    # Current step index
    current_step: int
    # Scratchpad for variable storage
    scratchpad: dict
```

### 3.2 Core Nodes (The Logic)

1.  **`planner_node`**:
    *   *Input:* User objective + History.
    *   *Action:* Calls Gemini Pro to decompose the task into steps.
    *   *Output:* Updates `state['plan']`.
    
2.  **`tool_node`**:
    *   *Input:* `state['plan'][current_step]`.
    *   *Action:* Selects the correct tool (e.g., `write_file`, `search_docs`). Executes it inside the validated block.
    *   *Output:* Adds a `ToolMessage` to `state['messages']`.

3.  **`reflector_node`**:
    *   *Input:* The result of the tool execution.
    *   *Action:* Checks if the step was influential or failed. Decides if we need to retry or move to the next step.

### 3.3 Folder Structure Strategy
*   `src/core/`: Base classes (`BaseTool`, `LLMClient` wrapper).
*   `src/agent/`: The graph definition (`graph.py`) and node logic (`nodes.py`).
*   `src/tools/`: Actual implementations of tools (`files.py`, `doc_generator.py`).

## 4. Implementation Phases (Step-by-Step Guide)

### Phase 1: Foundation & "Hello World"
1.  **Environment:** Set up `poetry`, install deps. Create `.env` for `GOOGLE_API_KEY`.
2.  **LLM Client:** Create `src/core/llm.py`. Implement a wrapper around `ChatGoogleGenerativeAI`. Add a simple test to ensure you can ping Gemini.
3.  **Logging:** proper `structlog` setup in `src/core/logger.py` to see JSON logs.

### Phase 2: The Tool Registry
1.  **Base Class:** Define `ToolInterface` in `src/core/tools.py` using Pydantic for `args_schema`.
2.  **File Tool:** Implement `WriteFileTool` and `ReadFileTool` in `src/tools/filesystem.py`. 
    *   *Constraint:* Ensure they check paths to prevent directory traversal attacks (e.g., `../`).
3.  **Unit Tests:** Write tests in `tests/unit/test_tools.py` to verify tools fail correctly on bad inputs.

### Phase 3: The Brain (LangGraph)
1.  **State Definition:** Define generic `AgentState` in `src/agent/state.py`.
2.  **Nodes:** Implement plain python functions for `call_model` and `execute_tool`.
3.  **Graph Construction:** In `src/agent/graph.py`, wire the nodes:
    *   `workflow.add_node("agent", call_model)`
    *   `workflow.add_node("action", tool_node)`
    *   `workflow.set_entry_point("agent")`
    *   `workflow.add_conditional_edges(...)` — If tool called -> go to action, else -> end.

### Phase 4: Production Hardenining
1.  **Dockerize:** Create `Dockerfile` that copies `src/` and installs specific deps.
2.  **Observability:** Add tracing (you can use `LangSmith` or just detailed logging) to see *exactly* what prompted the LLM.
3.  **CLI:** Create `src/main.py` using `typer` or `argparse` to run the agent from command line: `python src/main.py "Build a snake game"`

## 5. Docker vs Local Strategy
*   **Dev Mode:** Run locally (using `poetry run python...`) to develop faster. Be careful not to let the agent delete your home directory.
*   **Prod Mode:** Run with `docker-compose up`. Mount a volume:
    ```yaml
    volumes:
      - ./workspace_data:/app/workspace
    ```
    This ensures the agent can ONLY modify files inside `./workspace_data`.
