import pytest
from unittest.mock import MagicMock, patch, ANY

# Mock imports that might happen at module level for main.py
# conftest.py handles Cocoa, but we might need more specific mocks here

class TestZeroAppDelegate:
    
    @pytest.fixture
    def app_delegate(self):
        # We need to import inside the test or patch before import if main.py does heavy lifting at top level.
        # main.py imports ZeroPanel, ZeroWebView, HotKeyManager at top level.
        # These need to be mocked to avoid real GUI creation.
        
        with patch('main.ZeroPanel') as MockPanel, \
             patch('main.ZeroWebView') as MockWebView, \
             patch('hotkey.HotKeyManager') as MockHKM:
            
            # Setup mock instances
            mock_panel_instance = MockPanel.alloc().init()
            mock_panel_instance.contentView.return_value.bounds.return_value = ((0,0), (100,100))
            
            from main import ZeroAppDelegate
            delegate = ZeroAppDelegate.alloc().init()
            
            # Inject mocks that might be created in applicationDidFinishLaunching_
            # But wait, applicationDidFinishLaunching_ creates them.
            # So we just instantiate the delegate here.
            
            return delegate

    def test_launch_sequence(self, app_delegate):
        """Test the initialization logic in applicationDidFinishLaunching_"""
        notification = MagicMock()
        
        with patch('main.ZeroPanel') as MockPanel, \
             patch('main.ZeroWebView') as MockWebView, \
             patch('hotkey.HotKeyManager') as MockHKM, \
             patch('main.NSStatusBar') as MockStatusBar, \
             patch('main.NSMenu') as MockMenu:
            
            app_delegate.applicationDidFinishLaunching_(notification)
            
            # Verify Status Bar
            MockStatusBar.systemStatusBar().statusItemWithLength_.assert_called()
            
            # Verify Window Creation
            MockPanel.alloc().init.assert_called()
            
            # Verify WebView Creation
            MockWebView.alloc().initWithFrame_.assert_called()
            
            # Verify Hotkey Registration
            # We expect 2 hotkeys: Toggle Window (1) and Ghost Mode (2)
            assert app_delegate.hotkey_manager.register_hotkey.call_count == 2
            
    def test_ghost_mode_toggle(self, app_delegate):
        """Test toggling ghost mode."""
        # Manually verify the callback logic
        app_delegate.webview = MagicMock()
        app_delegate.is_ghost_mode = False
        
        # 1. Turn ON
        app_delegate.callback_ghost_mode()
        assert app_delegate.is_ghost_mode == True
        app_delegate.webview.toggle_ghost_mode.assert_called_once()
        
        # 2. Turn OFF
        app_delegate.callback_ghost_mode()
        assert app_delegate.is_ghost_mode == False
        assert app_delegate.webview.toggle_ghost_mode.call_count == 2

    def test_window_toggle_logic(self, app_delegate):
        """Test showing/hiding the window."""
        app_delegate.panel = MagicMock()
        
        # Case 1: Window is Visible -> Hide it
        app_delegate.panel.isVisible.return_value = True
        app_delegate.toggleWindow_(None)
        app_delegate.panel.orderOut_.assert_called_once()
        
        # Case 2: Window is Hidden -> Show it
        app_delegate.panel.reset_mock()
        app_delegate.panel.isVisible.return_value = False
        app_delegate.toggleWindow_(None)
        app_delegate.panel.makeKeyAndOrderFront_.assert_called_once()
