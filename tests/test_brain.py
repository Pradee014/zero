import time
import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
from orchestrator.runner import ZeroBrain

def on_brain_response(response: str):
    print(f"\n[CALLBACK] Brain finished thinking!")
    print(f"Response: {response}")

def main():
    print("Zero: Initializing Brain...")
    brain = ZeroBrain()
    
    print("Zero: Sending request: 'Hello World' with Context: VS Code")
    brain.process(
        input_text="Hello World", 
        context_data={"app": "VS Code", "title": "test_brain.py"}, 
        callback=on_brain_response
    )
    
    # Simulate the Main Thread/RunLoop staying alive
    print("Zero: Main thread continuing... (Brain should run in background)")
    for i in range(3):
        print(f"Main Thread Tick {i+1}...")
        time.sleep(1)

    print("Zero: Done.")

if __name__ == "__main__":
    main()
