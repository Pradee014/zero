import sys
import os
import time

# Ensure src is in path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from brain.memory import get_memory_client

def test_memory():
    print("Zero: Starting Memory Integration Test...")
    
    # 1. Initialize
    mem = get_memory_client()
    if not mem:
        print("FAIL: Could not initialize MemoryManager.")
        return

    user_id = "test-user-001"
    
    # 2. Add a Fact
    fact = "The user prefers using pytest for all testing frameworks."
    print(f"Adding fact: '{fact}'")
    mem.add(fact, user_id=user_id, metadata={"source": "test_script"})
    
    # Wait for async processing (Mem0 or vector store might need a moment)
    time.sleep(2)
    
    # 3. Search for Fact
    query = "What testing framework should I use?"
    print(f"Searching for: '{query}'")
    results = mem.search(query, user_id=user_id)
    
    print("\nResults:")
    found = False
    for r in results:
        print(f"- {r}")
        if "pytest" in r.lower():
            found = True
            
    if found:
        print("\nSUCCESS: Retrieved relevant memory!")
    else:
        print("\nFAIL: Did not retrieve the expected memory.")

if __name__ == "__main__":
    test_memory()
