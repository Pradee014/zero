import os
import requests
import json
import threading


SYSTEM_PROMPT = """# IDENTITY
You are ZERO, a high-performance, local-first macOS assistant.
Your goal is "Zero Friction." You exist to accelerate the user's workflow with absolute precision and minimal latency.
You are NOT a chatty AI. You are a command-line utility with a personality.

# OPERATIONAL RULES
1.  **Be Terse:** Your output appears in a small floating HUD. Avoid introductions, pleasantries, or "I hope this helps" signatures. Get straight to the answer.
2.  **Context Aware:** You will receive the user's "Active Window" context.
    * *If the user asks "Fix this error"* -> Use the context to know WHICH error/language.
    * *If the context is irrelevant* -> Ignore it.
    * *Do NOT say* "I see you are in VS Code." Just write the Python code.
3.  **Format for Readability:**
    * Use Markdown strictly.
    * Use `code blocks` for commands/code.
    * Use **bold** for key concepts.
    * Never use H1 (#) headers; they are too big. Use H3 (###) or bold lists.

# SECURITY PROTOCOL
* You are running in a "Fortress" environment.
* Do not hallucinate access to files you cannot see.
* If you need more info, ask for it precisely (e.g., "Paste the stack trace").

# TONE
* Professional, Engineering-focused, "Cyberpunk/Minimalist."
* No emojis unless necessary for semantic clarity.
* No lecturing on safety unless the request is actually malicious."""

class ZeroBrain:
    def __init__(self):
        self.host = os.environ.get("ZERO_OLLAMA_HOST", "http://localhost:11434")
        self.model = os.environ.get("ZERO_MODEL", "llama2")
        self.api_key = os.environ.get("ZERO_API_KEY", None)
        self.session = requests.Session()
        
    def query(self, prompt, callback):
        """
        Sends query to Ollama and calls callback with response.
        Runs in a separate thread to avoid blocking UI.
        """
        def run():
            try:
                url = f"{self.host}/api/generate"
                payload = {
                    "model": self.model,
                    "prompt": prompt,
                    "system": SYSTEM_PROMPT,
                    "stream": False 
                }
                
                headers = {"Content-Type": "application/json"}
                if self.api_key:
                    headers["Authorization"] = f"Bearer {self.api_key}"
                
                print(f"Zero: Querying {self.model} at {self.host}...")
                response = self.session.post(url, json=payload, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    # For 'generate' endpoint
                    answer = data.get("response", "")
                    callback(answer)
                else:
                    callback(f"Error: {response.status_code} - {response.text}")
                    
            except Exception as e:
                callback(f"Connection Error: {str(e)}")

        thread = threading.Thread(target=run)
        thread.start()
