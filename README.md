# 🤖 LangGraph AI Agent — Playground

> A fully functional, tool-augmented AI agent built with **LangGraph** + **Claude (Anthropic)**, running on a custom graph architecture.

---

## 📐 Agent Graph Architecture

```
         ┌─────────────────────────────────────────────┐
         │                   START                     │
         └──────────────────────┬──────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │    user_input_node    │  ◄──────────────────┐
                    └───────────┬───────────┘                     │
                                │                                 │
               ┌────────────────┴───────────────┐                 │
               │       (conditional edge)       │                 │
               ▼                                ▼                 │
             [END]                   ┌─────────────────────┐      │
        (user typed exit)            │     model_node      │      │
                                     └──────────┬──────────┘      │
                                                │                 │
                          ┌─────────────────────┴──────────┐      │
                          │       (conditional edge)       │      │
                          ▼                                ▼      │
                  [user_input_node] ◄──────  ┌─────────────────────┐
                  (no tool call)             │     tool_node       │
                                             └─────────────────────┘
                                                  (runs tool,
                                                loops back to model)
```

---

## 🛠️ Available Tools

| Tool | Description |
|------|-------------|
| `fetch_url` | Fetches and parses readable content from a webpage |
| `read_file` | Reads a file from disk |
| `list_files` | Lists files/directories in a given path |
| `create_file` | Creates a new file with given content |
| `edit_file` | Replaces the content of an existing file |
| `execute_bash` | Executes a bash command and returns output |

---

## 📁 Project Structure

```
LangGraph/
├── main.py               # Entry point — builds and runs the agent graph
├── state.py              # AgentState TypedDict definition
├── node_builder.py       # Factory functions for graph nodes
├── edge_builder.py       # Factory functions for conditional edges
├── tools/
│   ├── tool.py           # Tool dataclass + Anthropic param serializer
│   ├── tools.py          # Raw tool handler implementations
│   └── tools_factory.py  # Builds Tool instances with schemas
├── requirements.txt      # Python dependencies
└── .env                  # API keys (not committed)
```

---

## 🔄 How It Works

1. **`user_input_node`** — Waits for user input from the terminal
2. **`model_node`** — Sends the conversation history to Claude with bound tools
3. **`tool_node`** — If Claude decides to call a tool, this node executes it
4. The result is fed back to Claude, which continues reasoning
5. When Claude responds without a tool call, control returns to the user

---

## 💡 Key Design Decisions

- **Tool schema is manually defined** using Anthropic's `tool_param` format for full control
- **Conditional edges** cleanly separate routing logic from node logic
- **`AgentState`** is minimal — just a list of messages, keeping the graph stateless-friendly
- **`execute_bash`** tool gives the agent real system-level capabilities 🔥

---

## 📝 Notes

- The agent runs in a **loop** until the user types an exit command
- All tool handlers are pure functions in `tools/tools.py` — easy to test and extend
- Adding a new tool = implement handler → build `Tool` instance → add to `build_tools()`

---

*Auto-generated README with ❤️ by the agent itself — because why not?* 🤖
