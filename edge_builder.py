from langchain_core.messages import AIMessage, HumanMessage
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
        last_message: AIMessage = state["messages"][-1]
        message_content = last_message.content if isinstance(last_message.content, list) else []
        tool_blocks = [
            block
            for block in message_content
            if isinstance(block, dict) and block.get("type") == "tool_use"
        ]

        return "user_input_node" if not tool_blocks else "tool_node"

    return model_to_tool_edge
