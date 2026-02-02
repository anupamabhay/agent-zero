# Agent Zero: Technical Specification & User Manual

## 1. Introduction

**Agent Zero** is a production-grade **Autonomous AI Agent** designed to go beyond simple text generation. Unlike traditional chatbots, Agent Zero is an action-oriented system built on a **cyclic LangGraph architecture**. It perceives goals, plans execution steps, interacts with the filesystem and external tools, observes results, and iterates until the task is complete.

It serves as a "Generalist Assistant" capable of coding, research, planning, and system interaction, all while operating within a secure, persistent environment.

---

## 2. Features

*   **Action-Oriented Architecture**: Built on LangGraph to support cyclic "Think -> Act -> Observe" loops, allowing for error correction and complex multi-step tasks.
*   **Docker Sandbox**: All file operations and code execution occur within a secure Docker container, isolating the agent from the host system to prevent accidental damage.
*   **Persistent Memory**:
    *   **Short-term**: Maintains conversation context and state across the execution loop.
    *   **Long-term**: Stores facts and user preferences in a JSON-based memory system (`agent_memory.json`) for recall across different sessions.
*   **Web Research**: Equipped with tools to search the web (DuckDuckGo) and scrape website content for real-time information gathering.
*   **Git & Project Integration**: Can clone repositories, analyze project structures, track git history, and generate scrum reports.
*   **Resource Management**: Manages a personal knowledge base of links and resources with automatic summarization.

---

## 3. Getting Started

### Prerequisites
To run Agent Zero, ensure your system meets the following requirements:
*   **Python 3.13+**
*   **Poetry** (Dependency Manager)
*   **Docker** (For the sandbox environment)

### Configuration
Agent Zero uses a `.env` file for configuration. Create this file in the project root and set the following variables (defined in `src/config.py`):

| Variable | Description | Required | Default |
| :--- | :--- | :--- | :--- |
| `GOOGLE_API_KEY` | Your Google AI Studio API Key for Gemini models. | **Yes** | - |
| `GEMINI_MODEL` | The model version to use (e.g., `gemini-3-flash`, `gemini-3-pro-preview`). | No | `gemini-3-flash` |
| `WORKSPACE_ROOT` | The local directory to mount as the agent's workspace. | No | `./workspace` |
| `LOG_LEVEL` | Logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`). | No | `INFO` |

---

## 4. Tool Documentation

Agent Zero is equipped with a diverse set of tools categorized by function. Below is a guide to what each tool does and how to invoke it.

### 📂 Filesystem Operations
*   **`write_file`**: Writes text content to a specific file. Overwrites if the file exists.
    *   *Prompt:* "Create a python script named `hello.py` that prints 'Hello World'."
*   **`read_file`**: Reads and displays the contents of a file.
    *   *Prompt:* "Read the contents of `requirements.txt`."
*   **`list_files`**: Lists all files and directories in a specific path.
    *   *Prompt:* "Show me the files in the `src` directory."

### 🌐 Web & Research
*   **`search_web`**: Performs a web search using DuckDuckGo.
    *   *Prompt:* "Search for the latest features in Python 3.13."
*   **`scrape_website`**: Extracts text content from a specific URL.
    *   *Prompt:* "Read this article: https://example.com/article and summarize it."
*   **`get_youtube_transcript`**: Retrieves the full transcript of a YouTube video.
    *   *Prompt:* "Get the transcript for this video: https://youtube.com/watch?v=..."

### 🛠️ Project & Git
*   **`ingest_external_source`**: Clones a GitHub repository or extracts a ZIP file into the workspace.
    *   *Prompt:* "Clone the repository https://github.com/user/repo.git into `my_project`."
*   **`explore_project`**: Recursively maps out the file structure of a directory.
    *   *Prompt:* "Analyze the structure of the `backend` folder."
*   **`get_repo_history`**: Retrieves the latest git commit logs.
    *   *Prompt:* "What were the last 5 commits in this repo?"
*   **`get_file_diffs`**: Shows current uncommitted changes in the repository.
    *   *Prompt:* "Show me what files have been modified but not committed."
*   **`generate_scrum_report`**: Generates a structured status update based on project context.
    *   *Prompt:* "Write a scrum report based on the recent changes."

### 🧠 Memory & Knowledge
*   **`store_fact`**: Saves a piece of information to long-term memory.
    *   *Prompt:* "Remember that I prefer using Pytest for testing."
*   **`retrieve_fact`**: Recalls a specific fact from memory.
    *   *Prompt:* "What testing framework did I say I prefer?"
*   **`list_all_facts`**: Displays all stored facts.
    *   *Prompt:* "List everything you know about my preferences."
*   **`add_resource`**: Adds a URL to the resource knowledge base (auto-summarized).
    *   *Prompt:* "Save this link to my resources: https://docs.python.org/3/"
*   **`list_resources`**: Lists saved resources, optionally filtered by category.
    *   *Prompt:* "Show me my saved Python resources."

### 📅 Planning & System
*   **`create_routine`**: Generates a daily schedule based on a list of tasks and deadlines.
    *   *Prompt:* "Create a study schedule for Math (deadline Friday) and History (deadline Monday)."
*   **`execute_command`**: Runs a shell command in the workspace (Secure).
    *   *Prompt:* "Run `ls -la` in the current directory."
*   **`open_in_app`**: Opens a workspace file in a host application (e.g., Notepad, VS Code). *Note: Requires running on host, not Docker.*
    *   *Prompt:* "Open `notes.md` in Notepad."

---

## 5. Operational Guidelines

To ensure the best experience and security, follow these guidelines:

1.  **File-First Communication**:
    *   Agent Zero is designed to work with files. Instead of asking it to print 500 lines of code to the console, ask it to **"Write the code to `script.py`"**. This prevents context window overflow and makes the output immediately usable.

2.  **Content Purity**:
    *   The agent is optimized to provide direct answers and actions. It minimizes "meta-comments" (e.g., "I will now do this...") and focuses on executing the requested tools and providing the final result.

3.  **Security & Sandbox**:
    *   **Always** run untrusted or complex tasks within the Docker container.
    *   The `workspace_root` is the **only** directory the agent can access. Attempts to access files outside this directory (e.g., `../../system32`) are blocked by the `_get_safe_path` security check.

---

## 6. Troubleshooting

*   **Rate Limits (429 Errors)**:
    *   If you encounter API errors from Google Gemini, wait a few moments before retrying. The `gemini-3-flash` model generally has higher rate limits than Pro versions.
*   **Path Violations**:
    *   If the agent reports a "Security Violation," it is trying to access a file outside the defined `WORKSPACE_ROOT`. Ensure your prompt directs the agent to work within the allowed directory (e.g., `./workspace`).
*   **Docker Connection Issues**:
    *   Ensure the Docker daemon is running (`docker ps`). If the agent cannot connect, try restarting the Docker service.
