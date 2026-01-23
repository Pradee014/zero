import sys
import os

# Ensure we can import from src/tools
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from orchestrator.state import AgentState
from tools import ALL_TOOLS

def agent_node(state: AgentState):
    """
    The main agent node that calls the LLM with tools.
    """
    messages = state['messages']
    
    # Context Injection
    context = state.get('context', {})
    app_name = context.get('app', 'Unknown App')
    title = context.get('title', 'Unknown Title')
    
    # System Prompt
    system_prompt = (
        f"You are Zero, an intelligent AI agent integrated into macOS. "
        f"Current App: {app_name}. Window Title: {title}. "
        f"You have access to local tools (Calendar, Mail) and cloud tools (Notion, Trello, GitHub). "
        f"Use them to fulfill the user's request. "
        f"For security, ask for confirmation before destructive actions (though tools should handle safety). "
        f"Keep responses concise."
    )
    
    # Prepend System Message if not present
    if not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=system_prompt)] + messages
    
    # Model
    # Manufacturer: OpenAI Compatible (Ollama Cloud supports /v1/)
    model_name = os.getenv("ZERO_MODEL", "llama3.2")
    base_url = os.getenv("ZERO_OLLAMA_HOST", "http://localhost:11434")
    api_key = os.getenv("ZERO_API_KEY", "EMPTY") # OpenAI client needs a key, use placeholder if missing
    
    # If host is ollama.com, ensure /v1 is used if not present
    if "ollama.com" in base_url and "/v1" not in base_url:
        base_url = f"{base_url}/v1"

    model = ChatOpenAI(
        model=model_name,
        temperature=0,
        base_url=base_url,
        api_key=api_key
    )
    model_with_tools = model.bind_tools(ALL_TOOLS)
    
    response = model_with_tools.invoke(messages)
    
    return {"messages": [response]}

def build_zero_graph():
    """
    Constructs the Zero Orchestrator Graph with Tool Use.
    """
    workflow = StateGraph(AgentState)
    
    # Add Nodes
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", ToolNode(ALL_TOOLS))
    
    # Set Entry Point
    workflow.set_entry_point("agent")
    
    # Add Edges
    workflow.add_conditional_edges(
        "agent",
        tools_condition,
    )
    workflow.add_edge("tools", "agent")
    
    # Compile
    app = workflow.compile()
    return app
