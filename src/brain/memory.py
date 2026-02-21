import os
import threading
from typing import Dict, Any, List
from mem0 import Memory

class MemoryManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(MemoryManager, cls).__new__(cls)
                    cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """
        Initializes the Mem0 client with Qdrant as the vector store.
        """
        # Load Configuration
        self.user_id = os.getenv("MEM0_USER_ID", "zero-user")
        
        # 1. Vector Store Config (Qdrant)
        # Default to local path: src/brain/data/qdrant
        default_qdrant_path = os.path.join(os.path.dirname(__file__), "data", "qdrant")
        qdrant_path = os.getenv("QDRANT_PATH", default_qdrant_path)
        qdrant_url = os.getenv("QDRANT_URL")
        qdrant_api_key = os.getenv("QDRANT_API_KEY")

        # Construct Vector Store Config
        vector_store_config = {
            "provider": "qdrant",
            "config": {}
        }

        if qdrant_url:
            vector_store_config["config"]["url"] = qdrant_url
            if qdrant_api_key:
                vector_store_config["config"]["api_key"] = qdrant_api_key
        else:
            # Local Mode
            # Ensure directory exists
            os.makedirs(qdrant_path, exist_ok=True)
            vector_store_config["config"]["path"] = qdrant_path
            print(f"Zero: Using Local Qdrant at {qdrant_path}")

        # 2. LLM Config (for Fact Extraction)
        # Uses OpenAI-compatible API (e.g., OpenAI, Groq if compatible)
        # Mem0 defaults to OpenAI.
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
             # Fallback: Try GROQ key if using compatible endpoint, but Mem0 might enforce OpenAI client.
             # For now, we assume OPENAI_API_KEY is present or user will provide it.
             print("Zero: WARNING - OPENAI_API_KEY not found. Mem0 might fail.")
        
        llm_config = {
            "provider": "openai",
            "config": {
                "model": os.getenv("ZERO_MEM0_MODEL", "gpt-4o-mini"),
                "api_key": openai_api_key
            }
        }

        # 3. Initialize Mem0
        self.config = {
            "vector_store": vector_store_config,
            "llm": llm_config
        }
        
        try:
            self.memory = Memory.from_config(self.config)
            print("Zero: Memory Manager Initialized (Mem0 + Qdrant)")
        except Exception as e:
            print(f"Zero: Failed to initialize Memory: {e}")
            self.memory = None

    def add(self, content: str, user_id: str = None, metadata: Dict = None):
        """
        Adds a memory (interaction) to the system.
        """
        if not self.memory: return
        
        target_user = user_id or self.user_id
        try:
            self.memory.add(content, user_id=target_user, metadata=metadata)
        except Exception as e:
            print(f"Zero: Error adding memory: {e}")

    def search(self, query: str, user_id: str = None, limit: int = 5) -> List[str]:
        """
        Searches for relevant memories.
        Returns a list of strings (facts).
        """
        if not self.memory: return []

        target_user = user_id or self.user_id
        try:
            results = self.memory.search(query, user_id=target_user, limit=limit)
            # Result format from Mem0: [{'memory': 'fact...', 'score': ...}]
            return [r.get('memory', '') for r in results]
        except Exception as e:
            print(f"Zero: Error searching memory: {e}")
            return []

    def get_all(self, user_id: str = None) -> List[str]:
         """
         Retrieves all memories for the user.
         """
         if not self.memory: return []
         target_user = user_id or self.user_id
         try:
             results = self.memory.get_all(user_id=target_user)
             return [r.get('memory', '') for r in results]
         except Exception as e:
             print(f"Zero: Error getting all memories: {e}")
             return []

# Global Accessor
def get_memory_client() -> MemoryManager:
    return MemoryManager()
