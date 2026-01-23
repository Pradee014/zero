from typing import TypedDict, Annotated, List, Dict
from langchain_core.messages import BaseMessage
import operator

class AgentState(TypedDict):
    """
    The shared state (Clipboard) for all agents in the Zero system.
    """
    # Conversation history. 
    # operator.add allows us to just return NEW messages and have them appended automatically.
    messages: Annotated[List[BaseMessage], operator.add]
    
    # Context data from the "Senses" (e.g., {'app': 'VS Code', 'title': 'main.py'})
    # This is overwritten by the system, not appended.
    context: Dict[str, str]
    
    # Routing key to determine which agent runs next.
    # set by the Router node.
    next_agent: str
