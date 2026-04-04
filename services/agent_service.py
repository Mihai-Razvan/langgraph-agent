import os
from dotenv import load_dotenv

from langchain.chat_models import init_chat_model
from langchain_anthropic.chat_models import ChatAnthropic
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.runnables.base import RunnableBinding
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph

from state import AgentState
from tools.tool import Tool
from tools.tools_factory import build_tools
from node_builder import create_model_node, create_tool_node
from edge_builder import create_model_to_end_or_tool_edge

class Agent:
    def __init__(self):
        load_dotenv()
        self.ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
        self.agent_graph: StateGraph = StateGraph(AgentState)
        self.compiled_agent_graph: CompiledStateGraph | None = None
        self._init_agent()

    def _create_model_with_tools(self, available_tools: list[Tool]) -> RunnableBinding:
        model: ChatAnthropic = init_chat_model(
            "claude-sonnet-4-6",
            model_provider="anthropic",
            temperature=0,
            api_key=self.ANTHROPIC_API_KEY,
        )

        return model.bind_tools([tool.to_anthropic_tool_param() for tool in available_tools])

    def _init_agent(self):
        available_tools: list[Tool] = build_tools()
        model_with_tools: RunnableBinding = self._create_model_with_tools(available_tools)

        # Create and add nodes
        model_node = create_model_node(model_with_tools=model_with_tools)
        tool_node = create_tool_node(available_tools=available_tools)

        agent_graph: StateGraph = StateGraph(AgentState)
        agent_graph.add_node("model_node", model_node)
        agent_graph.add_node("tool_node", tool_node)

        # Create and add edges
        model_to_end_or_tool_node = create_model_to_end_or_tool_edge()

        agent_graph.add_edge(START, "model_node")
        agent_graph.add_conditional_edges(
            "model_node",
            model_to_end_or_tool_node,
            [END, "tool_node"]
        )
        agent_graph.add_edge("tool_node", "model_node")

        # Compile the agent, create the initial state and start the agent/
        checkpointer: InMemorySaver = InMemorySaver()
        self.compiled_agent_graph: CompiledStateGraph = agent_graph.compile(checkpointer=checkpointer)

    def _serialize_content(self, content):
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            serialized_blocks = []
            for block in content:
                if isinstance(block, dict):
                    serialized_blocks.append(dict(block))
                else:
                    serialized_blocks.append({"type": "text", "text": str(block)})
            return serialized_blocks
        return str(content)

    def _get_message_role(self, message: BaseMessage) -> str:
        if isinstance(message, HumanMessage):
            content = message.content
            if isinstance(content, list) and any(
                isinstance(block, dict) and block.get("type") == "tool_result"
                for block in content
            ):
                return "tool"
            return "user"
        if isinstance(message, AIMessage):
            return "assistant"
        if isinstance(message, ToolMessage):
            return "tool"

        message_type = getattr(message, "type", None)
        if message_type == "human":
            return "user"
        if message_type == "ai":
            return "assistant"
        if message_type == "tool":
            return "tool"
        return message_type or message.__class__.__name__.lower()

    def _serialize_message(self, message: BaseMessage) -> dict:
        serialized_message = {
            "id": getattr(message, "id", None),
            "role": self._get_message_role(message),
            "content": self._serialize_content(message.content),
        }

        if isinstance(message, AIMessage):
            tool_calls = []

            for block in getattr(message, "content_blocks", []):
                if isinstance(block, dict) and block.get("type") == "tool_use":
                    tool_calls.append({
                        "id": block.get("id"),
                        "name": block.get("name"),
                        "input": block.get("input"),
                    })

            if tool_calls:
                serialized_message["tool_calls"] = tool_calls

        return serialized_message

    def _extract_result(self, messages: list[BaseMessage]) -> str | None:
        for message in reversed(messages):
            if isinstance(message, AIMessage):
                return message.content

        return None

    def invoke(self, user_message: str, thread_id: int):
        initial_state: AgentState = {
            "messages": [HumanMessage(content=user_message)]
        }

        config: RunnableConfig = {
            "configurable": {
                "thread_id": thread_id
            }
        }

        result = self.compiled_agent_graph.invoke(initial_state, config=config)
        messages = result.get("messages", [])

        return {
            "thread_id": thread_id,
            "result": self._extract_result(messages),
            "messages": [self._serialize_message(message) for message in messages]
        }