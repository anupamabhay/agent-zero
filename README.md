# Agent Zero

**Agent Zero** is a production-grade **Autonomous AI Agent**. Unlike standard chatbots that just generate text, Agent Zero generates **actions**. It perceives a goal, breaks it down into plans, executes tools (file manipulation, coding), observes the results, and iterates until the job is done.

Built with **LangGraph** (State Machine), **Google Gemini 3**, and **Docker** (Sandboxing).

---

## 🚀 Key Features

*   **🧠 Cyclic Reasoning Engine:** Uses a "Think → Act → Observe" loop (ReAct pattern) powered by LangGraph, allowing for error recovery and complex planning.
*   **🛡️ Secure Sandbox:** All execution happens inside an isolated Docker container. The agent can only modify files in the mounted `workspace_data/` directory, protecting your host OS.
*   **⚡ Gemini 3 Powered:** optimized for the latest Gemini 3 Flash/Pro models with massive context windows (1M+ tokens).
*   **📁 File System Tools:** Native capabilities to Write, Read, and List files with path traversal security checks.
*   **🔍 Type Safety:** Built on Pydantic for rigorous data validation and structured output.

## 🛠️ Architecture

Agent Zero follows a cyclic graph architecture:
1.  **Reason:** The LLM analyzes the state and plans the next move.
2.  **Router:** Decides whether to act (call a tool) or finish (respond to user).
3.  **Execute:** Runs the tool in the Docker sandbox.
4.  **Observe:** Captures the tool output and feeds it back into the "Reason" node.

---

## ⚡ Getting Started

### Prerequisites
*   Docker Desktop installed and running.
*   A [Google AI Studio](https://aistudio.google.com/) API Key.

### 1. Setup Environment
Clone the repository and create your secrets file:

```bash
cp .env.example .env
```
Open `.env` and paste your API key:
```ini
GOOGLE_API_KEY=your_key_here
GEMINI_MODEL=gemini-3-flash-preview
LOG_LEVEL=INFO
```

### 2. Run with Docker (Recommended)
The safest and easiest way to run Agent Zero is via Docker Compose. This builds the environment and mounts your local `workspace_data` folder.

```bash
docker compose run --build agent-zero
```

### 3. Usage
Once the `>>` prompt appears, you can assign tasks:

*   **Coding:** *"Create a Python script to calculate Fibonacci numbers and save it to fib.py"*
*   **Data:** *"Read the data.csv file and summarize the columns"*
*   **System:** *"List all files in the current directory"*

To exit, type `quit`.

---

## 📂 Project Structure

```text
agent-zero/
├── src/
│   ├── agent/         # LangGraph logic (The Brain)
│   ├── core/          # State definitions and LLM factory
│   ├── tools/         # Tool definitions (Filesystem, etc.)
│   ├── config.py      # Configuration management
│   └── main.py        # Entry point
├── workspace_data/    # Shared folder between Host and Docker
├── Dockerfile         # Container definition
├── docker-compose.yml # Container orchestration
└── pyproject.toml     # Python dependencies
```
