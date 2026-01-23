from typing import TypedDict, Literal, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

# Define the State
class AgentState(TypedDict):
    last_message: str
    active_app: str
    next_agent: Literal["DEV", "CHAT", "router"]
    response: str

# ----------------- NODES -----------------

def router_node(state: AgentState):
    """
    The Brain / Central Hub.
    Decides which agent should handle the request.
    """
    message = state.get("last_message", "").lower()
    app = state.get("active_app", "")
    
    # Logic (Ported from original "Traffic Cop")
    # TODO: Replace with LLM Classifier
    if app == "VS Code" or "code" in message or "refactor" in message:
        return {"next_agent": "DEV"}
    
    return {"next_agent": "CHAT"}

def dev_agent(state: AgentState):
    """
    Placeholder for Dev-0.
    """
    return {"response": "[Dev-0] I'm ready to code. (Placeholder)"}

def chat_agent(state: AgentState):
    """
    Placeholder for Zero Prime / Chat.
    """
    return {"response": "[Zero Prime] How can I help? (Placeholder)"}

# ----------------- EDGES -----------------

def route_decision(state: AgentState) -> Literal["dev_agent", "chat_agent"]:
    """
    Determines the next node based on the 'next_agent' key.
    """
    if state["next_agent"] == "DEV":
        return "dev_agent"
    return "chat_agent"


# ----------------- GRAPH -----------------

builder = StateGraph(AgentState)

# Add Nodes
builder.add_node("router", router_node)
builder.add_node("dev_agent", dev_agent)
builder.add_node("chat_agent", chat_agent)

# Add Edges
builder.add_edge(START, "router")

# Conditional Edge from Router to Agents
builder.add_conditional_edges(
    "router",
    route_decision,
    {
        "dev_agent": "dev_agent",
        "chat_agent": "chat_agent"
    }
)

# Agents return to END (for now)
builder.add_edge("dev_agent", END)
builder.add_edge("chat_agent", END)

# Compile with Memory Persistence (Zero Latency)
memory = MemorySaver()
graph = builder.compile(checkpointer=memory)
