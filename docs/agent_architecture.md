---
tags: [project, engineering, agent-zero, langgraph, python, architecture, design-patterns, implementation-guide]
created: 2026-01-14
updated: 2026-01-16
type: technical-specification
status: production-ready
---

# Project: Agent Zero - Master Architecture & Implementation Guide

## 1. Introduction & Design Philosophy

### 1.1 What is "Agent Zero"?
**Agent Zero** is a prototype for a production-grade **Autonomous AI Agent**. Unlike a chatbot (which generates text), an agent generates **actions**. It perceives a goal, breaks it down into steps, executes tools (running code, editing files), observes the results, and iterates until the goal is met.

### 1.2 The "Why" Behind the Architecture
When designing a system like this, we must solve three specific problems that standard software doesn't face:
1.  **Non-Deterministic Control Flow:** Standard code follows `A -> B -> C`. Agents follow `A -> (Think) -> B or C or A (Retry)`. We need a **State Machine**, not a linear script.
2.  **Safety & Containment:** If an agent can "write code," it can accidentally delete your hard drive. We need a **Sandbox** (Docker).
3.  **State Persistence:** Agents take time. We need a way to save the "brain state" (memory) so we can pause/resume execution.

---

## 2. High-Level Design (HLD)

The HLD provides the "30,000-foot view" of the system. In system design, we use **Block Diagrams** to show how data flows between major subsystems.

### 2.1 Architectural Diagram (Cyclic State Machine)

This is a **Cyclic Graph**. Notice how the arrows loop back. This "Loop" is the core of agentic behavior. 

`reason > state > router logic` is a fundamental design choice in state-based agents. In these systems, nodes (like "Reason") don't typically "talk" to each other directly; instead, they both talk to the **State**.


```mermaid
graph TD
    %% Nodes
    User(["User / Developer"])
    API[Interface Layer: CLI / REST API]
    
    subgraph Agent_Core [Agent Core: LangGraph]
        direction TB
        State[("Agent State: Short-term Memory")]
        Reason[Reasoning Node: Planning & Decision]
        Router{Router Logic}
        Execute[Tool Node: Action Execution]
    end
    
    subgraph Resources [External Resources]
        LLM[Google Gemini 3]
        Docker[Docker Sandbox]
    end

    %% Simple Connections (Removing complex labels to prevent errors)
    User --> API
    API --> State
    
    State --> Reason
    Reason <--> LLM
    Reason --> State
    
    State --> Router
    Router -->|Action| Execute
    Router -->|Finished| API
    
    Execute <--> Docker
    Execute --> State
    
    %% The Loop
    Execute -.-> Reason
```

**Flow Explanation:**

1.  **Initialization:** The `User` submits a request via the `API` (CLI). This initializes the `Agent State` with the user's message.
2.  **Reasoning:** The `Reason` node (the brain) receives the current `State` and queries `Google Gemini 3` (LLM) to decide on the next step.
3.  **Decision:** The `Router` evaluates the LLM's response.
    *   If the LLM requests a tool call (e.g., "write_file"), the flow moves to `Execute`.
    *   If the LLM provides a final answer, the flow returns to the `API` and the user.
4.  **Execution:** The `Execute` node runs the requested tool inside the secure `Docker Sandbox`.
5.  **Observation:** The result of the tool execution (success or error) is written back to the `State` (Memory).
6.  **Loop:** The flow cycles back to the `Reason` node. The LLM sees the new state (including the tool output) and decides what to do next. This repeats until the goal is achieved.

### 2.2 Component Breakdown

This table details every major component, its responsibility, and the technology choice.

| Component | Technology | Responsibility | Design Rationale (Why?) |
| :--- | :--- | :--- | :--- |
| **Orchestrator** | **LangGraph** | Manages the "State Machine". Decides which node runs next. Handles loops and persistence. | Standard chains (LangChain) are linear (DAGs). Agents need loops. LangGraph is built specifically for cyclic graphs. |
| **Intelligence** | **Google Gemini** | The "Brain". Parses user intent, plans steps, and formats tool calls. | Gemini 3 has a massive context window (1M+ tokens), allowing it to read entire codebases in one shot. |
| **Runtime** | **Docker** | The "Body". Executes the actual file changes and shell commands. | **Security.** A mounted volume (`./workspace`) ensures the agent can *only* touch files we explicitly allow, protecting the host OS. |
| **Interface** | **Python/Typer** | CLI entry point. Handles arguments and output formatting. | Simple, typed, and robust for command-line tools. |
| **Validation** | **Pydantic** | Validates data entering and leaving the agent. | LLMs output text. Code needs types. Pydantic bridges this gap, preventing "hallucinated" arguments from crashing the app. |
| **Package Mgr** | **Poetry 2.0** | Manages Python dependencies and virtual environments. | Ensures **Reproducibility**. `pip freeze` is often insufficient. Poetry locks exact versions to avoid "it works on my machine" bugs. |

### 2.3 Key Technology Explanations

Here is a deeper look at the specific tools chosen and their roles in the architecture.

#### Interface: Python & Typer
*   **The Technology:** [Typer](https://typer.tiangolo.com/) is a modern library for building CLI applications based on standard Python type hints.
*   **Responsibility:** It serves as the **Entry Point** (Front-End). It parses command-line arguments, validates user input before the agent starts, and handles output formatting (colors, spinners) to improve the user experience.
*   **Rationale:** It is **Simple, Typed, and Robust**. By using Python types, it catches errors early (e.g., passing a string when an integer is needed) and auto-generates `--help` documentation.

#### Orchestrator: LangGraph
*   **The Technology:** A library specifically designed for building stateful, multi-actor applications with LLMs.
*   **Responsibility:** It manages the **Control Flow**. Unlike a standard script, it handles the "loops" where the agent tries, fails, and retries. It also manages **State Persistence**, allowing the agent to remember what happened 5 steps ago.
*   **Rationale:** Standard chains are linear (Start -> End). Agents are cyclic (Start -> Think -> Act -> Think ...). LangGraph makes building these loops intuitive and reliable.

#### Runtime: Docker
*   **The Technology:** The industry standard for containerization.
*   **Responsibility:** It provides a **Secure Sandbox**. The agent executes its code changes inside a container, isolated from your actual computer.
*   **Rationale:** **Safety.** If the agent accidentally runs `rm -rf /`, it only deletes the temporary container, not your operating system.

#### Validation: Pydantic
*   **The Technology:** The most widely used data validation library for Python.
*   **Responsibility:** It acts as the **Bridge** between the fuzzy text of an LLM and the strict code of the application. It forces the LLM's output to conform to specific schemas.
*   **Rationale:** **Reliability.** It prevents "hallucinated" arguments from crashing the application by validating data types at runtime.

---

## 3. Low-Level Design (LLD) & Project Structure

This section explains *how* we structure the code and *why*.

### 3.1 Project Structure Strategy
We follow a **Layered Architecture**. Each layer has a distinct responsibility, preventing "Spaghetti Code".

```text
agent-zero/
├── pyproject.toml       # The "Project Manifest". Defines dependencies and metadata.
├── Dockerfile           # The "Blueprint" for the safe runtime environment.
├── .env                 # Secrets (API Keys). Never committed to Git.
└── src/                 # The Source Code.
    ├── main.py          # Entry Point. The "Key" that starts the engine.
    ├── config.py        # Configuration Layer. Validates environment variables.
    ├── core/            # Core Domain. Things shared by the whole app (LLM, State).
    ├── agent/           # Application Logic. The LangGraph definitions (Brain).
    └── tools/           # Infrastructure Layer. The actual functions (File I/O).
```

### 3.2 The State Schema (`AgentState`)

The `AgentState` is the single source of truth for the agent's memory during a run. It is passed from node to node.

**Why TypedDict?** It provides compile-time checking. If we try to access `state["msgs"]` instead of `state["messages"]`, our editor will warn us.

| Field Name | Data Type | Description |
| :--- | :--- | :--- |
| `messages` | `list[BaseMessage]` | The conversation history. Contains `HumanMessage`, `AIMessage` (thoughts), and `ToolMessage` (results). |
| `step_count` | `int` | Tracks iterations to prevent infinite loops (Circuit Breaker pattern). |

**Code Representation:**
```python
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    # 'add_messages' is a specific reducer. It tells LangGraph: 
    # "Don't overwrite this list; APPEND new items to it."
    # It also handles deduplication of message IDs.
    messages: Annotated[list, add_messages]
    step_count: int
```

---

## 4. Implementation Guide (Step-by-Step)

This section contains the exact steps to build the system from scratch.

### Phase 1: Foundation & Setup

**Goal:** Create a reproducible, secure environment.

#### Step 1: Initialize Project (Poetry 2.0)
**Concept:** We use the modern `pyproject.toml` standard (PEP 621). This ensures our project structure is compatible with standard Python tools, not just Poetry.

**Commands:**
```bash
mkdir agent-zero
cd agent-zero
poetry init -n
poetry add langgraph langchain-google-genai pydantic-settings structlog python-dotenv
```

**File: `pyproject.toml` (Verify this structure):**
```toml
[project]
name = "agent-zero"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "langgraph",
    "langchain-google-genai",
    "pydantic-settings",
    "structlog",
]
```

#### Step 2: Configuration (`src/config.py`)
**Concept:** **Fail Fast.** We use `Pydantic Settings` to validate configuration on startup. If the API key is missing, the app crashes immediately with a clear error, rather than failing silently 10 minutes later.

```python
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr

class Settings(BaseSettings):
    # SecretStr hides the value in logs automatically (Security Best Practice)
    google_api_key: SecretStr
    gemini_model: str = "gemini-3"
    workspace_root: str = "./workspace"  # The Sandbox Root

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
```

### Phase 2: The Core Logic

**Goal:** Build the "Brain" and "Hands".

#### Step 3: The LLM Factory (`src/core/llm.py`)
**Concept:** **Dependency Injection.** We wrap the LLM creation in a function. This allows us to easily swap Gemini for another model later, or inject a "Mock LLM" for testing.

```python
from langchain_google_genai import ChatGoogleGenerativeAI
from src.config import settings

def get_llm():
    """
    Returns a configured LLM instance.
    Temperature=0 ensures the agent is deterministic (consistent) in its tool usage.
    """
    return ChatGoogleGenerativeAI(
        model=settings.gemini_model,
        google_api_key=settings.google_api_key.get_secret_value(),
        temperature=0
    )
```

#### Step 4: Secure Tool Registry (`src/tools/filesystem.py`)
**Concept:** **Sandboxing.** The agent is untrusted. We must implement "Path Traversal Prevention". If the agent asks to write to `../../WINDOWS/system32`, we must block it.

```python
from pathlib import Path
from langchain_core.tools import tool
from src.config import settings

@tool
def write_file(filename: str, content: str) -> str:
    """
    Writes content to a file. 
    Input: relative path (e.g. 'main.py').
    """
    # 1. Resolve the absolute path of the sandbox root
    safe_root = Path(settings.workspace_root).resolve()
    
    # 2. Resolve the target path
    target_path = (safe_root / filename).resolve()
    
    # 3. SECURITY CHECK: Does the target path start with the safe root?
    if not str(target_path).startswith(str(safe_root)):
        return "Error: Security Violation. You cannot write outside the workspace."
        
    try:
        # 4. Create directories if they don't exist
        target_path.parent.mkdir(parents=True, exist_ok=True)
        # 5. Write the file
        target_path.write_text(content, encoding="utf-8")
        return f"Successfully wrote to {filename}"
    except Exception as e:
        return f"Error writing file: {e}"
```

### Phase 3: The Graph Construction

**Goal:** Wire the nodes together into a runnable application.

#### Step 5: The Graph Definition (`src/agent/graph.py`)
**Concept:** **Orchestration.** We define the "Flow" of the application here.
*   **Nodes** do the work.
*   **Edges** define the flow.
*   **Conditional Edges** make decisions (Branching Logic).

```python
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from src.core.state import AgentState
from src.core.llm import get_llm
from src.tools.filesystem import write_file

# 1. Define Tools
tools_list = [write_file]
llm = get_llm()

# 2. Bind Tools to LLM (giving it "Hands")
# This forces the LLM to output JSON matching the tool schema
llm_with_tools = llm.bind_tools(tools_list)

# 3. Define the Reason Node (The Brain)
def reason_node(state: AgentState):
    # Input: List of messages
    # Output: New AIMessage (Thought or Tool Call)
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

# 4. Define the Router Logic (The Traffic Cop)
def router(state: AgentState):
    # Check the LAST message
    last_msg = state["messages"][-1]
    
    # If the LLM wants to call a tool, go to 'tools'
    if last_msg.tool_calls:
        return "tools"
    # Otherwise, we are done
    return END

# 5. Build the Graph
workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("reason", reason_node)
workflow.add_node("tools", ToolNode(tools_list)) # Prebuilt execution node

# Add Edges (Connections)
workflow.add_edge(START, "reason")
workflow.add_conditional_edges("reason", router)
workflow.add_edge("tools", "reason") # THE LOOP: Action -> Observation -> Reason

# Compile
app = workflow.compile()
```

### Phase 4: Production & Deployment

**Goal:** Run this safely in Docker.

#### Step 6: The Entry Point (`src/main.py`)
**Concept:** **Interface.** This file handles the user loop. It initializes the state and streams the output from the graph.

```python
import asyncio
from src.agent.graph import app

async def main():
    print("Agent Zero Initialized. Type 'quit' to exit.")
    
    while True:
        user_input = input(">> ")
        if user_input.lower() in ["quit", "exit"]:
            break
            
        # Initialize state with user input
        initial_state = {"messages": [("user", user_input)]}
        
        # Run the graph (Stream results)
        async for event in app.astream(initial_state):
            for key, value in event.items():
                print(f"\n--- Node: {key} ---")
                # Print the last message content for debugging
                print(value["messages"][-1].pretty_repr())

if __name__ == "__main__":
    asyncio.run(main())
```

#### Step 7: Docker Configuration (`docker-compose.yml`)
**Concept:** **Isolation.** This is the final safety barrier. Even if our Python code has a bug, the Docker container limits the blast radius.

```yaml
services:
  agent-zero:
    build: .
    # Mount the 'workspace' directory. 
    # The agent can destroy anything inside './workspace_data' on your host,
    # but it CANNOT touch your C:\ drive or other project files.
    volumes:
      - ./workspace_data:/app/workspace
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
    # Keep container running for interactive mode
    stdin_open: true 
    tty: true
```

---

## 5. Development Cheat Sheet

### Common Concepts & Terminology
*   **ReAct Pattern:** **Re**ason + **Act**. The loop of "Thought -> Action -> Observation".
*   **System Prompt:** The "Prime Directive". A hidden message sent at the start telling the agent "You are a coding assistant. Be concise."
*   **Temperature:** Randomness setting. 0.0 = Precise/Code. 0.7 = Creative/Writing.
*   **Context Window:** The short-term memory limit (e.g., 1M tokens). If history exceeds this, the agent "forgets" the start.

### Debugging Guide
| Symptom | Probable Cause | Fix |
| :--- | :--- | :--- |
| **Agent Loops Forever** | LLM keeps trying the same failing tool. | Add a `step_count` check in the router to force exit after N steps. |
| **"Tool Not Found"** | Tool name in `@tool` docstring doesn't match binding. | Ensure function name matches exactly. Use clear docstrings. |
| **Access Denied Error** | Path traversal check failed. | Check `workspace_root` in `.env` and ensure the agent is using relative paths. |

---
*For details on Generative AI theory, refer to: "Gen AI & LLMs in Engineering > AI, ML"*
