import os
import requests
import json
import threading

class ZeroBrain:
    def __init__(self):
        self.host = os.environ.get("ZERO_OLLAMA_HOST", "http://localhost:11434")
        self.model = os.environ.get("ZERO_MODEL", "llama2")
        self.api_key = os.environ.get("ZERO_API_KEY", None)
        
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
                    "stream": False 
                }
                
                headers = {"Content-Type": "application/json"}
                if self.api_key:
                    headers["Authorization"] = f"Bearer {self.api_key}"
                
                print(f"Zero: Querying {self.model} at {self.host}...")
                response = requests.post(url, json=payload, headers=headers, timeout=30)
                
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
