import os
from dotenv import load_dotenv

from langchain.chat_models import init_chat_model
from langchain_anthropic.chat_models import ChatAnthropic
from langchain_core.runnables import RunnableConfig
from langchain_core.runnables.base import RunnableBinding
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph

from state import AgentState
from tools.tool import Tool
from tools.tools_factory import build_tools
from node_builder import create_model_node, create_user_input_node, create_tool_node
from edge_builder import create_user_input_to_model_edge, create_model_to_user_input_or_tool_edge

def save_graph_image(compiled_agent_graph: CompiledStateGraph, output_path: str = "agent_graph.png") -> None:
    png_bytes = compiled_agent_graph.get_graph(xray=True).draw_mermaid_png()
    with open(output_path, "wb") as graph_file:
        graph_file.write(png_bytes)

def main():
    def create_model_with_tools(available_tools: list[Tool]) -> RunnableBinding:
        model: ChatAnthropic = init_chat_model(
            "claude-sonnet-4-6",
            model_provider="anthropic",
            temperature=0,
            api_key=ANTHROPIC_API_KEY,
        )

        return model.bind_tools([tool.to_anthropic_tool_param() for tool in available_tools])

    load_dotenv()
    ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

    available_tools: list[Tool] = build_tools()

    model_with_tools: RunnableBinding = create_model_with_tools(available_tools)

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
    model_to_user_input_or_tool_node = create_model_to_user_input_or_tool_edge()

    agent_graph.add_edge(START, "user_input_node")
    agent_graph.add_conditional_edges(
        "user_input_node",
        user_input_to_model_node,
        ["model_node", END]
    )
    agent_graph.add_conditional_edges(
        "model_node",
        model_to_user_input_or_tool_node,
        ["user_input_node", "tool_node"]
    )
    agent_graph.add_edge("tool_node", "model_node")

    # Compile the agent, create the initial state and start the agent/
    checkpointer: InMemorySaver = InMemorySaver()
    compiled_agent_graph: CompiledStateGraph = agent_graph.compile(checkpointer=checkpointer)
    initial_state: AgentState = {
        "messages": []
    }

    save_graph_image(compiled_agent_graph)

    config: RunnableConfig = {
        "configurable": {
            "thread_id": "1"
        }
    }
    compiled_agent_graph.invoke(initial_state, config=config)

    initial_state: AgentState = {
        "messages": []
    }
    compiled_agent_graph.invoke(initial_state, config=config)

if __name__ == "__main__":
    main()