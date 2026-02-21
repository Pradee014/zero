import pytest
from unittest.mock import MagicMock, patch
import os
from brain.memory import MemoryManager, get_memory_client

@pytest.fixture
def mock_mem0_class():
    with patch("brain.memory.Memory") as MockMemory:
        mock_instance = MagicMock()
        MockMemory.from_config.return_value = mock_instance
        yield MockMemory

@pytest.fixture
def memory_manager(mock_mem0_class):
    # Reset singleton
    MemoryManager._instance = None
    manager = MemoryManager()
    return manager

def test_singleton_pattern():
    MemoryManager._instance = None
    m1 = MemoryManager()
    m2 = get_memory_client()
    assert m1 is m2

def test_initialization_config(mock_mem0_class):
    MemoryManager._instance = None
    with patch.dict(os.environ, {"QDRANT_PATH": "/tmp/qdrant", "OPENAI_API_KEY": "sk-test"}):
        manager = MemoryManager()
        
        # Verify config passed to Memory.from_config
        args = mock_mem0_class.from_config.call_args[0][0] # first arg
        assert args["vector_store"]["config"]["path"] == "/tmp/qdrant"
        assert args["llm"]["config"]["api_key"] == "sk-test"

def test_add_memory(memory_manager, mock_mem0_class):
    memory_manager.add("User likes Python", user_id="test-user")
    mock_mem0_class.from_config.return_value.add.assert_called_once_with("User likes Python", user_id="test-user", metadata=None)

def test_search_memory(memory_manager, mock_mem0_class):
    mock_mem0_class.from_config.return_value.search.return_value = [
        {'memory': 'User likes Python', 'score': 0.9},
        {'memory': 'User is a developer', 'score': 0.8}
    ]
    
    results = memory_manager.search("What does user like?", user_id="test-user")
    assert len(results) == 2
    assert "User likes Python" in results
    assert "User is a developer" in results
    mock_mem0_class.from_config.return_value.search.assert_called_once_with("What does user like?", user_id="test-user", limit=5)

def test_get_all_memories(memory_manager, mock_mem0_class):
    mock_mem0_class.from_config.return_value.get_all.return_value = [{'memory': 'Fact 1'}]
    results = memory_manager.get_all(user_id="test-user")
    assert results == ['Fact 1']
    mock_mem0_class.from_config.return_value.get_all.assert_called_once_with(user_id="test-user")
