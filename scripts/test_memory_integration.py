import os
import sys
# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from brain.memory import get_memory_client
import time

def test_integration():
    print("Initializing Memory Client...")
    mem_client = get_memory_client()
    
    if not mem_client.memory:
        print("Memory client failed to initialize (check API keys/config).")
        return

    # 1. Add Fact
    fact = "My favorite color is #FF00FF"
    user_id = "test-integration-user"
    print(f"Adding fact: {fact}")
    mem_client.add(fact, user_id=user_id)
    
    # Wait for indexing (Mem0 might be async or Qdrant might need a moment)
    print("Waiting for indexing...")
    time.sleep(2)
    
    # 2. Search
    print("Searching for fact...")
    try:
        results = mem_client.search("What is my favorite color?", user_id=user_id)
        print(f"Results: {results}")
        
        # 3. Verify
        if any("FF00FF" in r for r in results):
            print("SUCCESS: Fact retrieved correctly.")
        else:
            print("FAILURE: Fact not found.")
    except Exception as e:
        print(f"Error searching: {e}")

if __name__ == "__main__":
    test_integration()
