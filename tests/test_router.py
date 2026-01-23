import unittest
from src.brain.router import router_node, AgentState

class TestRouterNode(unittest.TestCase):
    
    def test_vscode_context_routes_to_dev(self):
        """Active app VS Code should always route to DEV, regardless of message."""
        state: AgentState = {"last_message": "hello", "active_app": "VS Code"}
        self.assertEqual(router_node(state), "DEV")
        
        state_ignore: AgentState = {"last_message": "ignore context", "active_app": "VS Code"}
        self.assertEqual(router_node(state_ignore), "DEV")

    def test_keywords_route_to_dev(self):
        """Keywords 'code' or 'refactor' should route to DEV."""
        # Test 'code'
        state_code: AgentState = {"last_message": "write some python code", "active_app": "Finder"}
        self.assertEqual(router_node(state_code), "DEV")
        
        # Test 'refactor'
        state_refactor: AgentState = {"last_message": "please refactor this", "active_app": "Chrome"}
        self.assertEqual(router_node(state_refactor), "DEV")

    def test_default_chat(self):
        """Standard conversation should route to CHAT."""
        state: AgentState = {"last_message": "what is the weather?", "active_app": "Chrome"}
        self.assertEqual(router_node(state), "CHAT")
        
        state_empty: AgentState = {"last_message": "", "active_app": ""}
        self.assertEqual(router_node(state_empty), "CHAT")

if __name__ == "__main__":
    unittest.main()
