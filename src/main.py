import Cocoa
from Cocoa import (
    NSApplication,
    NSObject,
    NSStatusBar,
    NSVariableStatusItemLength,
    NSMenu,
    NSMenuItem,
    NSLog
)
from gui.window import ZeroPanel
from gui.webview import ZeroWebView
from dotenv import load_dotenv
import os
import subprocess
import re
from datetime import datetime
from database import db
from context.monitor import ContextMonitor

# Load env variables from .env file
load_dotenv()

class ZeroAppDelegate(NSObject):
    def applicationDidFinishLaunching_(self, notification):
        NSLog("Zero: Launching...")
        
        # 0. Initialize DB & Logging
        db.init_db()
        self.log_boot_time()
        
        # 0.1 Start Context Monitor
        self.monitor = ContextMonitor.alloc().initWithCallback_(self.on_context_update)
        # self.monitor.start() # MOVING TO END to avoid race condition
        
        # 0.2 Initialize Graph Brain
        from orchestrator.graph import build_zero_graph
        self.graph = build_zero_graph()
        
        # 1. Setup Status Bar
        self.status_item = NSStatusBar.systemStatusBar().statusItemWithLength_(NSVariableStatusItemLength)
        self.status_item.button().setTitle_("O")
        
        # Construct Menu
        menu = NSMenu.alloc().init()
        
        # Toggle Item
        toggle_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "Toggle Zero",
            "toggleWindow:",
            "0"
        )
        menu.addItem_(toggle_item)
        
        menu.addItem_(NSMenuItem.separatorItem())
        
        # Quit Item
        quit_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "Quit Zero",
            "terminate:",
            "q"
        )
        menu.addItem_(quit_item)
        
        self.status_item.setMenu_(menu)
        
        # 2. Setup Window
        self.panel = ZeroPanel.alloc().init()
        
        if not self.panel:
            NSLog("Zero: CRITICAL - Panel allocation failed!")
            return
        
        # 3. Setup WebView
        # Frame should match the window's content view
        content_view = self.panel.contentView()
        self.webview = ZeroWebView.alloc().initWithFrame_(content_view.bounds())
        
        # Connect Query Handler
        self.webview.on_query = self.on_user_query
        
        # Autoresize with window
        self.webview.setAutoresizingMask_(Cocoa.NSViewWidthSizable | Cocoa.NSViewHeightSizable)
        
        content_view.addSubview_(self.webview)
        
        # Window is hidden initially. Summon with Cmd+Shift+0
        # self.panel.makeKeyAndOrderFront_(None)
        self.panel.center()
        
        # 4. Setup Global Hotkey
        from hotkey import HotKeyManager, cmdKey, shiftKey
        self.hotkey_manager = HotKeyManager()
        
        # ID 1: Toggle Window (Cmd+Shift+0)
        self.hotkey_manager.register_hotkey(
            29, # '0'
            cmdKey | shiftKey,
            self.callback_toggle,
            1
        )

        # ID 2: Toggle Ghost Mode (Cmd+Shift+9)
        self.hotkey_manager.register_hotkey(
            25, # '9'
            cmdKey | shiftKey,
            self.callback_ghost_mode,
            2
        )

        self.is_ghost_mode = False
        
        # Start Monitor NOW that UI is ready
        self.monitor.start()
        
        NSLog("Zero: Ready.")

    def on_user_query(self, text):
        """
        Handle user query from WebView.
        Runs graph.stream() in a background thread.
        """
        import threading
        from langchain_core.messages import HumanMessage
        
        def run_graph():
            # 1. Fetch Context
            context = {
                'app': self.monitor.current_app,
                'title': self.monitor.current_title
            }
            
            # 2. Prepare Input
            inputs = {
                "messages": [HumanMessage(content=text)],
                "context": context
            }
            
            try:
                # 3. Stream Output
                # The graph returns events. We need to find the AIMessage chunks.
                # For our simple router_node, it returns a dict with 'messages'.
                # But since we are streaming, we might get updates.
                # Let's see how our graph is built.
                # Currently simple router returns a full AIMessage.
                
                # If we use .stream(), it yields state updates.
                for event in self.graph.stream(inputs):
                    # event is typically {'node_name': state_update}
                    for node, values in event.items():
                        if "messages" in values:
                            # Get the last message which is the response
                            last_msg = values["messages"][-1]
                            # Stream the content
                            self.webview.stream_response(last_msg.content)
                            
            except Exception as e:
                NSLog(f"Zero: Graph Error: {e}")
                self.webview.stream_response(f"**Error:** {str(e)}")
                
        # Launch Thread
        thread = threading.Thread(target=run_graph)
        thread.start()

    def callback_toggle(self):
        self.toggleWindow_(None)

    def callback_ghost_mode(self):
        # Toggle state
        self.is_ghost_mode = not self.is_ghost_mode
        
        # Toggle Native Shadow
        # Shadow is now always False natively, handled by CSSBoxShadow
        
        # Dispatch to webview to toggle CSS
        if self.webview:
            self.webview.toggle_ghost_mode()

    def toggleWindow_(self, sender):
        if self.panel.isVisible():
            self.panel.orderOut_(None)
            NSApplication.sharedApplication().hide_(None) # Also hide the app to return focus
        else:
            self.panel.makeKeyAndOrderFront_(None)
            self.panel.center()
            NSApplication.sharedApplication().activateIgnoringOtherApps_(True)

    def applicationWillTerminate_(self, notification):
        NSLog("Zero: Terminating...")
        # Force one last commit if we can, though tricky in terminate
        if hasattr(self, 'monitor'):
            self.monitor._commit_current_activity()

    def on_context_update(self, data):
        # Data is { 'app': str, 'title': str }
        # Update Status Bar (Optional, maybe debug only)
        # self.status_item.button().setTitle_(f"0 | {data['app']}")
        
        # Send to WebView
        if self.webview:
            self.webview.send_context_update(data)

    def log_boot_time(self):
        try:
            # Get boot time from sysctl
            # kern.boottime: { sec = 1737380000, usec = 123... }
            out = subprocess.check_output(["sysctl", "-n", "kern.boottime"]).decode('utf-8')
            match = re.search(r"sec = (\d+)", out)
            if match:
                boot_ts = int(match.group(1))
                boot_iso = datetime.fromtimestamp(boot_ts).isoformat()
                db.log_session_start(boot_iso)
        except Exception as e:
            NSLog(f"Zero: Error logging boot time: {e}")


if __name__ == "__main__":
    app = NSApplication.sharedApplication()
    delegate = ZeroAppDelegate.alloc().init()
    app.setDelegate_(delegate)
    
    # Hide from Dock (Ghost Mode)
    # NSApplicationActivationPolicyAccessory = 1
    app.setActivationPolicy_(1)
    
    from PyObjCTools import AppHelper
    AppHelper.runEventLoop()
