from typing import Literal
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from orchestrator.state import AgentState
import os
import json

def router_node(state: AgentState):
    """
    The Router Node.
    Classifies the user's intent and routes to the appropriate agent.
    """
    messages = state['messages']
    last_message = messages[-1]
    
    # If the last message is from an AI, we stop (or continue conversation in a more complex graph)
    # CRITICAL: This prompt must be extremely strict to prevent 'openai/gpt-oss-120b' from 
    # generating verbose "chain of thought" output which crashes the parser.
    # Do NOT relax these constraints without verifying against that specific model.
    # User Request: This feature must work at all costs.
    
    system_prompt = (
        "You are the Router for Project Zero. "
        "Your job is to classify the latest user request into one of the following categories: "
        "'OPS' - For scheduling, calendar, email, motion, trello, logistics, specific non-coding tasks. "
        "'DEV' - For coding, git, terminal, debugging, software engineering. "
        "'GENERAL' - For general chat, questions, or if unsure. "
        "IMPORTANT: You must respond with ONLY the category name. Do not explain. Do not think. Just output the code."
    )
    
    # Use a fast model for routing
    # Default to ZERO_MODEL if ZERO_ROUTER_MODEL isn't set, to ensure we use a model that exists.
    from orchestrator.llm_utils import get_llm
    
    default_model = os.getenv("ZERO_MODEL", "gpt-4o-mini")
    
    model = get_llm(default_model_name=default_model, model_env_var="ZERO_ROUTER_MODEL")
    
    # We only need the last user message for routing usually, but full context helps.
    # To save tokens, we might just send the last 2-3 messages.
    routing_messages = [SystemMessage(content=system_prompt)] + messages[-3:]
    
    response = model.invoke(routing_messages)
    classification = response.content.strip().upper()
    
    # Fallback if model talks too much
    if "OPS" in classification: classification = "OPS"
    elif "DEV" in classification: classification = "DEV"
    else: classification = "GENERAL"
        
    return {"classification": classification}

def route_dispatcher(state: AgentState) -> Literal["ops_agent", "dev_agent"]:
    """
    Edge logic to determine the next node based on classification.
    """
    classification = state.get("classification", "GENERAL")
    
    if classification == "OPS":
        return "ops_agent"
    else:
        # GENERAL falls back to DEV (Zero Prime) for now, as it's the main agent.
        return "dev_agent"
