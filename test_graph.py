import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from src.orchestrator.graph import build_zero_graph
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

def test_full_graph():
    load_dotenv()
    graph = build_zero_graph()
    inputs = {
        "messages": [HumanMessage(content="Draft an email to p.pradeepkumar014@gmail.com saying hello world and i am testing the system")],
        "context": {"app": "Terminal", "title": "test"}
    }
    
    for event in graph.stream(inputs):
        print("EVENT:", event)

if __name__ == "__main__":
    test_full_graph()
