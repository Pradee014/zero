import os
import sys

# Ensure src is in path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from langchain_core.messages import SystemMessage, HumanMessage
from src.orchestrator.llm_utils import get_llm
from src.tools.email_ops import email_ops

def test_tool_calling():
    print("Testing Tool Calling...")
    
    # Load env manually
    from dotenv import load_dotenv
    load_dotenv()
    
    model = get_llm(default_model_name="openai/gpt-oss-120b", model_env_var="ZERO_MODEL")
    model_with_tools = model.bind_tools([email_ops])
    
    messages = [
        SystemMessage(content="You are Ops-0. You have access to the email_tool. Use it to draft emails."),
        HumanMessage(content="draft an email to p.pradeepkumar014@gmail.com saying Hello world and that I am testing the system")
    ]
    
    print("\nInvoking model...")
    response = model_with_tools.invoke(messages)
    
    print("\n--- RESPONSE OUTPUT ---")
    print(f"Content: {response.content}")
    print(f"Tool Calls: {response.tool_calls}")

if __name__ == "__main__":
    test_tool_calling()
