## About

* Built with **LangGraph** (State), **Gemini** (Reason), and **Docker** (Sandbox).
* Uses a "Think → Act → Observe" loop (ReAct pattern) powered by LangGraph.
* All execution happens inside an isolated Docker container. The agent can only modify files in the mounted `workspace_data/` directory, protecting the host OS.
* Optimized for the latest Gemini 3 Flash/Pro models with massive context windows (1M+ tokens).
* Can Write, Read, and List files with path traversal security checks.
* Built on Pydantic for data validation and structured output.

## 🛠️ Architecture

Follows a cyclic graph architecture:
1.  **Reason:** LLM analyzes the state and plans the next move.
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
│   ├── agent/         # LangGraph logic (Brain)
│   ├── core/          # State definitions and LLM 
│   ├── tools/         # Tool definitions (Filesystem, etc.)
│   ├── config.py      # Configuration management
│   └── main.py        # Entry point
├── workspace_data/    # Shared folder between Host and Docker
├── Dockerfile         # Container definition
├── docker-compose.yml # Container orchestration
└── pyproject.toml     # Python dependencies
```
