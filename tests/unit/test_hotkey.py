import pytest
from unittest.mock import MagicMock, patch, call
import sys

# Ensure Cocoa is mocked before importing hotkey (already handled by conftest, but explicit import check is good)
from hotkey import HotKeyManager, cmdKey, shiftKey

class TestHotKeyManager:
    
    @pytest.fixture
    def manager(self):
        return HotKeyManager()

    def test_initialization(self, manager):
        assert manager.callbacks == {}
        assert manager.hot_key_refs == []

    def test_register_hotkey(self, manager):
        callback = MagicMock()
        
        # We need to verify that carbon functions are called.
        # Since we mocked them in conftest via ctypes.class.LoadLibrary,
        # we need to access that same mock object to assert calls.
        # But here we can just rely on the fact that logic proceeds without error
        # and internal state is updated.
        
        # Actually, to verify calls, we can inspect the manager's internal usage if we exposed the library,
        # OR we can patch `hotkey.carbon` directly in this test file if we want strict verification.
        
        with patch('hotkey.carbon') as mock_carbon:
            mock_carbon.GetApplicationEventTarget.return_value = 12345 # Fake target
            mock_carbon.RegisterEventHotKey.return_value = 0
            
            manager.register_hotkey(10, cmdKey, callback, 1)
            
            # Verify callback stored
            assert manager.callbacks[1] == callback
            
            # Verify Carbon calls
            mock_carbon.GetApplicationEventTarget.assert_called_once()
            mock_carbon.RegisterEventHotKey.assert_called_once()
            
            # Verify handler installation (called once)
            mock_carbon.InstallEventHandler.assert_called_once()

    def test_register_duplicate_handler_check(self, manager):
        """Ensure InstallEventHandler is only called once even for multiple hotkeys."""
        callback1 = MagicMock()
        callback2 = MagicMock()
        
        with patch('hotkey.carbon') as mock_carbon:
            mock_carbon.GetApplicationEventTarget.return_value = 1
            mock_carbon.RegisterEventHotKey.return_value = 0
            
            manager.register_hotkey(1, 0, callback1, 1)
            manager.register_hotkey(2, 0, callback2, 2)
            
            assert mock_carbon.InstallEventHandler.call_count == 1
            assert manager.callbacks[1] == callback1
            assert manager.callbacks[2] == callback2
