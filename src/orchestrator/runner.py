import asyncio
import threading
from typing import Dict, Any, Callable
from langchain_core.messages import HumanMessage
from .graph import build_zero_graph

class ZeroBrain:
    def __init__(self):
        self.graph = build_zero_graph()
        # We don't start the loop here; we start it per request or manage a long-running background loop
        # For simplicity in this phase, we'll run a new loop for each request in a thread (or share one)
        
    def process(self, input_text: str, context_data: Dict[str, str], callback: Callable[[str], None]):
        """
        Public Sync API called by the Mac App.
        Spins up a background thread to run the Async Graph.
        """
        # Create a thread to run the async operation
        thread = threading.Thread(
            target=self._run_async_logic, 
            args=(input_text, context_data, callback),
            daemon=True
        )
        thread.start()
        
    def _run_async_logic(self, input_text: str, context_data: Dict[str, str], callback: Callable[[str], None]):
        """
        The entry point for the background thread.
        Creates a new event loop for this thread and runs the graph.
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(self._ainvoke_graph(input_text, context_data))
            
            # When done, call the callback 
            # NOTE: required to happen on Main Thread? 
            # For logging/printing it's fine. For UI updates, PyObjC might need AppHelper.callAfter
            callback(result)
        finally:
            loop.close()
            
    async def _ainvoke_graph(self, input_text: str, context_data: Dict[str, str]) -> str:
        """
        The actual async invocation of LangGraph.
        """
        initial_state = {
            "messages": [HumanMessage(content=input_text)],
            "context": context_data,
            "next_agent": "router"
        }
        
        # Invoke the graph
        final_state = await self.graph.ainvoke(initial_state)
        
        # Extract response
        messages = final_state.get('messages', [])
        if messages:
             return messages[-1].content
        return "Zero Brain: No response."
