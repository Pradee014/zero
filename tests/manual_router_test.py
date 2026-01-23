
import sys
import os

# Ensure src is in path
sys.path.append(os.path.join(os.getcwd(), "src"))

from brain.router import graph

def test_routing():
    config = {"configurable": {"thread_id": "test_thread_1"}}
    
    # Test Case 1: Active App is VS Code -> Should route to DEV
    print("--- Test Case 1: VS Code Context ---")
    inputs = {"active_app": "VS Code", "last_message": "Make this faster"}
    result = graph.invoke(inputs, config=config)
    print(f"Result: {result.get('response')}")
    
    if "[Dev-0]" in result.get('response', ''):
        print("✅ Routed to Dev Agent")
    else:
        print("❌ Failed Routing (Expected Dev)")

    # Test Case 2: General Chat -> Should route to CHAT
    print("\n--- Test Case 2: General Chat ---")
    inputs = {"active_app": "Finder", "last_message": "Tell me a joke"}
    result = graph.invoke(inputs, config=config)
    print(f"Result: {result.get('response')}")
    
    if "[Zero Prime]" in result.get('response', ''):
        print("✅ Routed to Chat Agent")
    else:
        print("❌ Failed Routing (Expected Chat)")

    # Test Case 3: Code keyword in Message -> Should route to DEV
    print("\n--- Test Case 3: Code Intent ---")
    inputs = {"active_app": "Finder", "last_message": "Refactor this code"}
    result = graph.invoke(inputs, config=config)
    print(f"Result: {result.get('response')}")
    
    if "[Dev-0]" in result.get('response', ''):
        print("✅ Routed to Dev Agent")
    else:
        print("❌ Failed Routing (Expected Dev)")

if __name__ == "__main__":
    test_routing()
