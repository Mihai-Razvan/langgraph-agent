# Step 1: Define tools and model

import os
from dotenv import load_dotenv

from langchain.chat_models import init_chat_model
from langchain.tools import tool
from langchain.chat_models.base import BaseChatModel
from langchain_anthropic.chat_models import ChatAnthropic
from langchain_core.messages import HumanMessage
from langchain_core.runnables.base import RunnableBinding
from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph

from state import AgentState
from tools.tool import Tool
from tools.tools_factory import build_tools
from node_builder import create_model_node, create_user_input_node, create_tool_node
from edge_builder import create_user_input_to_model_edge, create_model_to_tool_edge

def main():
    def create_model_with_tools(available_tools_handlers) -> RunnableBinding:
        model: ChatAnthropic = init_chat_model(
            "claude-sonnet-4-6",
            model_provider="anthropic",
            temperature=0,
            api_key=ANTHROPIC_API_KEY,
        )

        return model.bind_tools(available_tools_handlers)

    load_dotenv()
    ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

    available_tools: list[Tool] = build_tools()
    available_tools_handlers = [tool.handler for tool in available_tools]

    model_with_tools: RunnableBinding = create_model_with_tools(available_tools_handlers)

    agent_graph: StateGraph = StateGraph(AgentState)

    # Create and add nodes
    model_node = create_model_node(model_with_tools=model_with_tools)
    user_input_node = create_user_input_node()
    tool_node = create_tool_node(available_tools=available_tools)

    agent_graph.add_node("model_node", model_node)
    agent_graph.add_node("user_input_node", user_input_node)
    agent_graph.add_node("tool_node", tool_node)

    # Create and add edges
    user_input_to_model_node = create_user_input_to_model_edge()
    model_to_tool_node = create_model_to_tool_edge()

    agent_graph.add_edge(START, "user_input_node")
    agent_graph.add_conditional_edges(
        "user_input_node",
        user_input_to_model_node,
        ["model_node", END]
    )
    agent_graph.add_conditional_edges(
        "model_node",
        model_to_tool_node,
        ["user_input_node", "tool_node"]
    )
    agent_graph.add_edge("tool_node", "model_node")

    # Compile the agent, create the initial state and start the agent/
    compiled_agent_graph: CompiledStateGraph = agent_graph.compile()
    initial_state: AgentState = {
        "messages": []
    }
    compiled_agent_graph.invoke(initial_state)


if __name__ == "__main__":
    main()




# Augment the LLM with tools
# tools = [add, multiply, divide]
# tools_by_name = {tool.name: tool for tool in tools}
# model_with_tools = model.bind_tools(tools)
#
# # Step 2: Define state
#
# from langchain.messages import AnyMessage
# from typing_extensions import TypedDict, Annotated
# import operator
#
#
# class MessagesState(TypedDict):
#     messages: Annotated[list[AnyMessage], operator.add]
#     llm_calls: int
#
# # Step 3: Define model node
# from langchain.messages import SystemMessage
#
#
# def llm_call(state: dict):
#     """LLM decides whether to call a tool or not"""
#
#     return {
#         "messages": [
#             model_with_tools.invoke(
#                 [
#                     SystemMessage(
#                         content="You are a helpful assistant tasked with performing arithmetic on a set of inputs."
#                     )
#                 ]
#                 + state["messages"]
#             )
#         ],
#         "llm_calls": state.get('llm_calls', 0) + 1
#     }
#
#
# # Step 4: Define tool node
#
# from langchain.messages import ToolMessage
#
#
# def tool_node(state: dict):
#     """Performs the tool call"""
#
#     result = []
#     for tool_call in state["messages"][-1].tool_calls:
#         tool = tools_by_name[tool_call["name"]]
#         observation = tool.invoke(tool_call["args"])
#         result.append(ToolMessage(content=observation, tool_call_id=tool_call["id"]))
#     return {"messages": result}
#
# # Step 5: Define logic to determine whether to end
#
# from typing import Literal
# from langgraph.graph import StateGraph, START, END
#
#
# # Conditional edge function to route to the tool node or end based upon whether the LLM made a tool call
# def should_continue(state: MessagesState) -> Literal["tool_node", END]:
#     """Decide if we should continue the loop or stop based upon whether the LLM made a tool call"""
#
#     messages = state["messages"]
#     last_message = messages[-1]
#
#     # If the LLM makes a tool call, then perform an action
#     if last_message.tool_calls:
#         return "tool_node"
#
#     # Otherwise, we stop (reply to the user)
#     return END
#
# # Step 6: Build agent
#
# # Build workflow
# agent_builder = StateGraph(MessagesState)
#
# # Add nodes
# agent_builder.add_node("llm_call", llm_call)
# agent_builder.add_node("tool_node", tool_node)
#
# # Add edges to connect nodes
# agent_builder.add_edge(START, "llm_call")
# agent_builder.add_conditional_edges(
#     "llm_call",
#     should_continue,
#     ["tool_node", END]
# )
# agent_builder.add_edge("tool_node", "llm_call")
#
# # Compile the agent
# agent = agent_builder.compile()
#
#
# from IPython.display import Image, display
#
# # Show the agent when Mermaid rendering is reachable; skip it in offline environments.
# try:
#     display(Image(agent.get_graph(xray=True).draw_mermaid_png()))
# except Exception as exc:
#     print(f"Skipping graph rendering: {exc}")
#
# # Invoke
# from langchain.messages import HumanMessage
# messages = [HumanMessage(content="Add 3 and 4.")]
# messages = agent.invoke({"messages": messages})
# for m in messages["messages"]:
#     m.pretty_print()
