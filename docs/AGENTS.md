# Agentic Architecture (The Brain)

Zero uses **LangGraph** to define its cognitive architecture. This allows for cyclical, stateful flows rather than simple request-response chains.

## 1. Orchestration Model

The core logic resides in `src/orchestrator/graph.py`.

### State
The `AgentState` tracks the conversation history and shared context:
```python
class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    context: dict  # { 'app': 'VS Code', 'title': 'main.py' }
```

### Nodes
*   **Router / Agent Node:** Determines the intent of the user. It looks at the input and the `context` to decide if it should:
    1.  Respond directly (Chat).
    2.  Call a Tool (e.g., Search, File I/O).
    3.  Delegate to a Sub-Agent (Planned).
*   **Tool Node:** Executes requested tools and returns the output to the graph.

## 2. Agent Capabilities (Planned)

We are evolving from a single "Generalist" model to a swarm of specialized agents:

### 🛠️ Engineer Agent
*   **Focus:** Code generation, file manipulation, terminal execution.
*   **Tools:** `read_file`, `write_file`, `run_terminal`, `grep`.
*   **Constraint:** Heavily sandboxed by `src/security.py`.

### 🔍 Research Agent
*   **Focus:** Information gathering and synthesis.
*   **Tools:** `browser_search`, `read_url`, `summarize_content`.
*   **Behavior:** Can perform multi-step research (Search -> Read -> Refine Search -> Read -> Answer).

### ⚡ Shortcuts Agent
*   **Focus:** OS automation.
*   **Tools:** AppleScript, Shortcuts.app triggers.

## 3. Streaming & Events

To ensure responsiveness, the graph acts as a generator.
1.  **Token Streaming:** LLM tokens are pushed to the frontend immediately via `webview.stream_response()`.
2.  **State Streaming:** Intermediate steps (e.g., "Searching web...", "Reading file...") are pushed as UI status updates.

## 4. Security "Airlock"

Zero is "Human-in-the-loop" by default for sensitive actions.

*   **ReadOnly Tools:** (Search, Read File) -> Allowed automatically.
*   **Side-Effect Tools:** (Write File, Run Command) -> Intercepted by `src/security.py`. The user must explicitly approve these actions if the confidence threshold is not met (future feature).
