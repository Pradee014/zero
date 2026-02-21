from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from orchestrator.state import AgentState
from tools import OPS_TOOLS
import os

def ops_agent_node(state: AgentState):
    """
    The Ops-0 (COO) Agent Node.
    Specializes in: Scheduling, Knowledge Management, Email, and Logistics.
    """
    messages = state['messages']
    context = state.get('context', {})
    
    # Specialized System Prompt for Ops-0
    system_prompt = (
        "You are Ops-0, the Chief Operating Officer of Project Zero. "
        "Your role is to handle logistics, scheduling, knowledge management, and communications. "
        "You have access to Notion, Google Calendar, Trello, and Email tools. "
        "Be efficient, organized, and professional. "
        "authentication is handled automatically by the system. DO NOT ask the user for API keys or tokens. Just call the tools directly."
        "When managing content, always check Notion first to see if it exists. "
        "When scheduling, always check for conflicts first."
    )
    
    # Prepend System Message if not present (or if different agent was last)
    # Ideally, the router sets the context, but we enforce it here.
    if not isinstance(messages[0], SystemMessage) or "Ops-0" not in messages[0].content:
         messages = [SystemMessage(content=system_prompt)] + messages

    # Use a potentially faster/cheaper model for Ops tasks if configured
    # Logic: Try ZERO_OPS_MODEL -> ZERO_MODEL -> default
    from orchestrator.llm_utils import get_llm
    
    # Resolve default model based on fallback chain for Ops
    fallback_model = os.getenv("ZERO_MODEL", "gpt-3.5-turbo")
    
    from brain.memory import get_memory_client
    from langchain_core.messages import HumanMessage

    # 1. Retrieve Context from Memory
    try:
        mem_client = get_memory_client()
        last_human_msg = next((m.content for m in reversed(messages) if isinstance(m, HumanMessage)), "")
        
        if last_human_msg:
            relevant_memories = mem_client.search(last_human_msg, limit=3)
            if relevant_memories:
                memory_block = "\n".join([f"- {m}" for m in relevant_memories])
                if "Ops-0" in messages[0].content:
                     # Modifying the System Message (messages[0])
                     # We reconstruct it to append memory
                     original_prompt = messages[0].content
                     if "[RECALLED MEMORIES]" not in original_prompt:
                        new_prompt = original_prompt + f"\n\n[RECALLED MEMORIES]\n{memory_block}\n"
                        messages[0] = SystemMessage(content=new_prompt)

    except Exception as e:
        print(f"Zero: Ops Memory Retrieval Failed: {e}")

    model = get_llm(default_model_name=fallback_model, model_env_var="ZERO_OPS_MODEL")
    
    model_with_tools = model.bind_tools(OPS_TOOLS)
    response = model_with_tools.invoke(messages)
    
    # 2. Store Interaction
    try:
        if last_human_msg:
            mem_client.add(last_human_msg, metadata={"agent": "ops-0"})
    except Exception as e:
        print(f"Zero: Ops Memory Storage Failed: {e}")

    return {"messages": [response]}
