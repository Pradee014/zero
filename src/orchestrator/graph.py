import sys
import os

# Ensure we can import from src/tools
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from orchestrator.state import AgentState
from tools import ALL_TOOLS, DEV_TOOLS, OPS_TOOLS
from orchestrator.agents.ops import ops_agent_node
from orchestrator.router import router_node, route_dispatcher

def dev_agent_node(state: AgentState):
    """
    The main/dev agent node that calls the LLM with tools.
    """
    messages = state['messages']
    
    # Context Injection
    context = state.get('context', {})
    app_name = context.get('app', 'Unknown App')
    title = context.get('title', 'Unknown Title')
    
    # System Prompt
    system_prompt = (
        f"You are Zero (Dev-0), an agentic AI coder. "
        f"Current App: {app_name}. Window Title: {title}. "
        f"You have access to coding tools (Git, Terminal) and general knowledge. "
        f"If the user asks for scheduling or logistics, refer them to Ops-0 (handled by router). "
        f"IMPORTANT: When using tools, output ONLY the tool call. Do not explain your thought process before calling a tool. "
        f"Do not wrap the tool call in markdown code blocks."
    )
    
    # Prepend System Message if not present
    if not isinstance(messages[0], SystemMessage) or "Dev-0" not in messages[0].content:
        messages = [SystemMessage(content=system_prompt)] + messages
    
    # Model
    # Use centralized LLM utility (supports Groq & Ollama)
    from orchestrator.llm_utils import get_llm
    from brain.memory import get_memory_client
    
    # 1. Retrieve Context from Memory
    try:
        mem_client = get_memory_client()
        # Use the last human message for query
        last_human_msg = next((m.content for m in reversed(messages) if isinstance(m, HumanMessage)), "")
        
        if last_human_msg:
            relevant_memories = mem_client.search(last_human_msg, limit=3)
            if relevant_memories:
                memory_block = "\n".join([f"- {m}" for m in relevant_memories])
                system_prompt += f"\n\n[RECALLED MEMORIES]\n{memory_block}\n"
    except Exception as e:
        print(f"Zero: Memory Retrieval Failed: {e}")

    # Update System Message with Memories
    if not isinstance(messages[0], SystemMessage) or "Dev-0" not in messages[0].content:
         messages = [SystemMessage(content=system_prompt)] + messages
    else:
        # If system message exists, append memory to it (hacky but works for now)
        # Better: Replace the system message. 
        # For this iteration, we just ensure the prompt includes it if we rebuilt it.
        # If we didn't rebuild, we might miss it. Let's force update 0.
        messages[0] = SystemMessage(content=system_prompt)

    model = get_llm(default_model_name="llama3.2", model_env_var="ZERO_MODEL")
    # Bind DEV tools specifically
    model_with_tools = model.bind_tools(DEV_TOOLS)
    
    response = model_with_tools.invoke(messages)
    
    # 2. Store Interaction in Memory (Async/Background ideally)
    # For now, synchronous to ensure it works.
    try:
        if last_human_msg:
            # We store the user's intent + the agent's response summary?
            # Mem0 fits best with "User Said X". 
            mem_client.add(last_human_msg, metadata={"app": app_name, "title": title})
    except Exception as e:
        print(f"Zero: Memory Storage Failed: {e}")
    
    return {"messages": [response]}

def general_agent_node(state: AgentState):
    """
    Agent for general conversation without tool bindings.
    """
    messages = state['messages']
    
    # System Prompt for General Chat
    system_prompt = (
        "You are Zero, a helpful AI assistant. "
        "You are engaging in general conversation. "
        "Do not try to call tools. Just answer the user's questions helpfuly."
    )
    
    if not isinstance(messages[0], SystemMessage) or "Zero" not in messages[0].content:
        messages = [SystemMessage(content=system_prompt)] + messages

    # Model without tools
    from orchestrator.llm_utils import get_llm
    model = get_llm(default_model_name="llama3.2", model_env_var="ZERO_MODEL")
    
    response = model.invoke(messages)
    return {"messages": [response]}

def build_zero_graph():
    """
    Constructs the Zero Orchestrator Graph with Tool Use.
    """
    workflow = StateGraph(AgentState)
    
    # Add Nodes
    # Add Nodes
    workflow.add_node("router", router_node)
    workflow.add_node("dev_agent", dev_agent_node)
    workflow.add_node("ops_agent", ops_agent_node)
    workflow.add_node("general_agent", general_agent_node)
    workflow.add_node("tools", ToolNode(ALL_TOOLS)) # Keep ALL tools available in tool node for now
    
    # Set Entry Point
    workflow.set_entry_point("router")
    
    # Add Edges
    # Router -> Agent
    workflow.add_conditional_edges(
        "router",
        route_dispatcher
    )
    
    # Agent -> Tools (Dev)
    workflow.add_conditional_edges(
        "dev_agent",
        tools_condition,
    )
    
    # Agent -> Tools (Ops)
    workflow.add_conditional_edges(
        "ops_agent",
        tools_condition,
    )
    
    # Tools -> Agent (Loop back)
    # Critical: Use the last sender to determine where to return?
    # For simplicity in LangGraph, ToolNode returns to a fixed node or we use conditional logic.
    # We need a "router" for return? Or just have tools return to a 'dispatcher' that checks context.
    # SIMPLIFICATION: For now, Tools return to 'router' (which re-evaluates) OR we hardcode return.
    # Let's use a "Any Agent" return strategy. 
    # Actually, standard pattern is agent -> tool -> agent.
    # We need separate tool nodes or a conditional edge from tools.
    
    workflow.add_edge("tools", "router") # Sending back to router is safest to re-orient context
    
    # Compile
    app = workflow.compile()
    return app
