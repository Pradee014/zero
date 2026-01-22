import pytest
from unittest.mock import MagicMock, patch
from network.client import ZeroBrain

class TestZeroBrain:
    
    @pytest.fixture
    def brain(self):
        """Fixture to initialize ZeroBrain with default settings."""
        # Ensure env vars don't interfere or are set as expected
        with patch.dict('os.environ', {'ZERO_OLLAMA_HOST': 'http://test-host', 'ZERO_MODEL': 'test-model'}):
            return ZeroBrain()

    def test_initialization(self, brain):
        assert brain.host == 'http://test-host'
        assert brain.model == 'test-model'

    def test_query_success(self, brain):
        """Test a successful query to the LLM."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "Hello, World!"}
        
        callback = MagicMock()
        
        # Patch session.post inside the brain instance
        with patch.object(brain.session, 'post', return_value=mock_response) as mock_post:
            
            with patch('threading.Thread') as mock_thread_cls:
                # Make the thread run immediately in the main thread for testing
                def side_effect(target, **kwargs):
                    target()
                    return MagicMock()
                
                mock_thread_cls.side_effect = side_effect
                
                brain.query("Hello", callback)
                
                # Check request
                mock_post.assert_called_once()
                args, kwargs = mock_post.call_args
                assert kwargs['json']['prompt'] == "Hello"
                assert kwargs['json']['model'] == "test-model"
                
                # Check callback
                callback.assert_called_once_with("Hello, World!")

    def test_query_failure(self, brain):
        """Test a failed query (non-200 status)."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        
        callback = MagicMock()
        
        with patch.object(brain.session, 'post', return_value=mock_response):
            with patch('threading.Thread') as mock_thread_cls:
                def side_effect(target, **kwargs):
                    target()
                    return MagicMock()
                mock_thread_cls.side_effect = side_effect
                
                brain.query("Hello", callback)
                
                callback.assert_called_once()
                assert "Error: 500" in callback.call_args[0][0]

    def test_query_exception(self, brain):
        """Test exception handling during query."""
        callback = MagicMock()
        
        with patch.object(brain.session, 'post', side_effect=Exception("Network Down")):
            with patch('threading.Thread') as mock_thread_cls:
                def side_effect(target, **kwargs):
                    target()
                    return MagicMock()
                mock_thread_cls.side_effect = side_effect
                
                brain.query("Hello", callback)
                
                callback.assert_called_once()
                assert "Connection Error: Network Down" in callback.call_args[0][0]
