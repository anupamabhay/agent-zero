from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from src.core.state import AgentState
from src.core.llm import get_llm
from src.tools.filesystem import write_file, read_file, list_files
from datetime import datetime

# Define tools and LLM
tools_list = [write_file, read_file, list_files]
llm = get_llm()

#  Bind tools to LLM
llm_with_tools = llm.bind_tools(tools_list)

# Ssytem Prompt
SYSTEM_PROMT = """You are Agent Zero, a versatile autonomous AI assistant.
Your goal is to complete the user's request efficiently, whether it involves data processing, content creation, or system operations.

GUIDELINES:
1. ANALYZE the request to understand the goal (e.g., "save a recipe", "summarize a file").
2. PLAN your steps. Do you need to read a file first? Or just write one?
3. USE TOOLS. You interact with the world via tools. Use 'write_file' to save output, 'read_file' to gather context, and 'list_files' to explore.
4. OBSERVE & ITERATE. If a tool fails (e.g., file not found), analyze the error and try a fix.
5. BE CONCISE. Focus on the action.
"""

# Define the Reason Node (Brain)
def reason_node(state: AgentState):
    current_date = datetime.now().strftime("%A, %d %B %Y")
    prompt_text = f"{SYSTEM_PROMT}\n\nCurrent Date: {current_date}"
    messages = [SystemMessage(content=prompt_text)] + state["messages"]
    response = llm_with_tools.invoke(messages)

    return {"messages": [response]} 


# Define the Router Logic
def router(state: AgentState):
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