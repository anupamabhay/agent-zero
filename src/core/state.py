"""
State definitions for LangGraph.
Defines the schema of the graph state (TypedDict or Pydantic).
"""
from typing import TypedDict, Annotated, List, Union

class AgentState(TypedDict):
    """
    The state of the agent as it traverses the graph.
    Attributes:
        input: User input
        chat_history: List of messages
        scratchpad: Internal reasoning steps
    """
    pass
