from typing import Any

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables.base import RunnableBinding
from state import AgentState
from tools.tool import Tool


def create_model_node(model_with_tools: RunnableBinding):
    def model_node(state: AgentState):
        model_response = model_with_tools.invoke(state["messages"])
        state["messages"].append(AIMessage(content_blocks=model_response.content_blocks))

        for block in model_response.content_blocks:
            print("Assistant: ", block)

        return state

    return model_node

def create_user_input_node():
    def user_input_node(state: AgentState):
        user_input = input("User: ")

        state["messages"].append(HumanMessage(content=user_input))

        return state

    return user_input_node

def create_tool_node(available_tools: list[Tool]):
    def tool_node(state: AgentState):
        last_message: HumanMessage = state["messages"][-1]
        tool_blocks = [block for block in last_message.content_blocks if block.get("type") == "tool_use"]
        response_content_blocks = []

        for block in tool_blocks:
            name : str = block.get("name")
            tool_input = block.get("input")
            tool_id = block.get("id")

            tool: Tool = next(
                (t for t in available_tools if t.name == name),
                None
            )

            if tool is None:
                raise ValueError(f"Tool '{name}' not found")

            tool_result: Any = tool.run(
                tool_name=name,
                **tool_input
            )

            response_block = {
                "tool_use_id": tool_id,
                "type": "tool_result",
                "content": tool_result
            }

            response_content_blocks.append(response_block)

        state["messages"].append(HumanMessage(content_blocks=response_content_blocks))

        return state

    return tool_node