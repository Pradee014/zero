from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from .state import AgentState

def router_node(state: AgentState):
    """
    A simple router/echo node for testing.
    In the future, this will use an LLM to decide the next agent.
    """
    messages = state['messages']
    last_message = messages[-1]
    
    # Simple Echo Logic
    context = state.get('context', {})
    app_name = context.get('app', 'Unknown App')
    
    response_text = f"Zero Brain: I see you are in {app_name}. You said: {last_message.content}"
    
    return {
        "messages": [AIMessage(content=response_text)],
        "next_agent": "end"
    }

def build_zero_graph():
    """
    Constructs the Zero Orchestrator Graph.
    """
    workflow = StateGraph(AgentState)
    
    # Add Nodes
    workflow.add_node("router", router_node)
    
    # Set Entry Point
    workflow.set_entry_point("router")
    
    # Add Edges
    # For now, Router -> End is the only path
    workflow.add_edge("router", END)
    
    # Compile
    app = workflow.compile()
    return app
