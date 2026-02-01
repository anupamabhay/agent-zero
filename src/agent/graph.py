from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from src.core.state import AgentState
from src.core.llm import get_llm
from src.tools.filesystem import write_file, read_file, list_files
from src.tools.web import search_web, scrape_website
from src.tools.system import execute_command
from src.tools.media import get_youtube_transcript
from src.tools.memory import store_fact, retrieve_fact, list_all_facts
from src.tools.github import ingest_external_source, get_repo_history, get_file_diffs
from src.tools.host import open_in_app
from datetime import datetime

# Define tools and LLM
tools_list = [
    write_file,
    read_file,
    list_files,
    search_web,
    scrape_website,
    execute_command,
    get_youtube_transcript,
    store_fact,
    retrieve_fact,
    list_all_facts,
    explore_project,
    generate_scrum_report,
    add_resource,
    list_resources,
    create_routine,
    ingest_external_source,
    get_repo_history,
    get_file_diffs,
    open_in_app,
]


llm = get_llm()

#  Bind tools to LLM
llm_with_tools = llm.bind_tools(tools_list)

# System Prompt
SYSTEM_PROMPT = """You are Agent Zero, a versatile autonomous AI assistant.
Your goal is to complete the user's request efficiently, whether it involves data processing, content creation, web research, or system operations.

COMMUNICATION GUIDELINES:
1. OUTPUT FORMAT: For long reports, routines, schedules, or complex code blocks, ALWAYS save the full output to a file in the workspace (e.g., 'daily-routine.md', 'project-summary.md'). 
2. TERMINAL BREVITY: In the terminal, provide a concise summary of what you did and mention the filename where the full details are saved.
3. FILE NAMING: Use intelligent, descriptive, and hyphenated filenames (e.g., 'scrum-report-feb-1.md').

OPERATIONAL GUIDELINES:
1. ANALYZE the request to understand the goal.
2. PLAN your steps. Decide which tools are needed (e.g., search first, then scrape, then write).
3. USE TOOLS. You interact with the world via tools. 
   - 'write_file', 'read_file', 'list_files' for file operations.
   - 'search_web', 'scrape_website' for internet research.
   - 'execute_command' for shell commands in the workspace.
   - 'get_youtube_transcript' for analyzing YouTube video content.
   - 'store_fact', 'retrieve_fact', 'list_all_facts' for persistent long-term memory.
   - 'explore_project' to recursively map a directory for reports/updates.
   - 'generate_scrum_report' to format project progress updates.
   - 'add_resource', 'list_resources' to manage and categorize links/resources.
   - 'create_routine' to generate realistic schedules based on tasks and deadlines.
   - 'ingest_external_source' to clone public GitHub repos or extract .zip files into the workspace.
   - 'get_repo_history' to read commit logs for status updates.
   - 'get_file_diffs' to see uncommitted changes.
   - 'open_in_app' to open a workspace file in a host application (Notepad, Obsidian, etc.).

4. OBSERVE & ITERATE. If a tool fails, analyze the result and try a different approach.
5. CONTEXTUAL MEMORY: You have a persistent memory of this session's messages. Do not "guess" or "re-read" files to find what was JUST discussed. Use the message history.
6. FILE CONTENT PURITY: Files you create (e.g., Markdown reports, routines) must contain ONLY the raw data/requested content. NEVER include meta-comments like "(updated by agent)", "(modified)", or conversational filler inside the file itself.
"""


# Define the Reason Node (Brain)
def reason_node(state: AgentState):
    current_date = datetime.now().strftime("%A, %d %B %Y")
    prompt_text = f"{SYSTEM_PROMPT}\n\nCurrent Date: {current_date}"
    messages = [SystemMessage(content=prompt_text)] + state["messages"]
    response = llm_with_tools.invoke(messages)

    # Increment step count
    step_count = state.get("step_count", 0) + 1

    return {"messages": [response], "step_count": step_count}


# Define the Router Logic
def router(state: AgentState):
    # Check for infinite loops
    if state.get("step_count", 0) > 15:
        return END

    last_msg = state["messages"][-1]

    if last_msg.tool_calls:
        return "tools"
    return END


# Build the State Graph
workflow = StateGraph(AgentState)

# Add nodes and edges
workflow.add_node("reason", reason_node)
workflow.add_node("tools", ToolNode(tools_list))

workflow.add_edge(START, "reason")
workflow.add_conditional_edges("reason", router)
workflow.add_edge("tools", "reason")

app = workflow.compile()
