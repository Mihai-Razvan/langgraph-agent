from langchain_core.messages import HumanMessage
from langgraph.graph import END

from state import AgentState


def create_user_input_to_model_edge():
    def user_input_to_model_edge(state: AgentState):
        last_message: HumanMessage = state["messages"][-1]
        last_message_content: str = last_message.content

        return END if (last_message_content.lower() == "stop") else "model_node"

    return user_input_to_model_edge

def create_model_to_tool_edge():
    def model_to_tool_edge(state: AgentState):
        last_message: HumanMessage = state["messages"][-1]
        tool_blocks = [block for block in last_message.content_blocks if block.get("type") == "tool_use"]

        return  "user_input_node" if (tool_blocks is None) else "tool_node"

    return model_to_tool_edge