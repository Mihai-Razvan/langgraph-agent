from typing import TypedDict, Any, Annotated
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    messages: Annotated[list[Any], add_messages]