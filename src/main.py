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
        # 0.2 Initialize Graph Brain
        from orchestrator.graph import build_zero_graph
        self.graph = build_zero_graph()
        self.current_conversation_id = None # Track active session
        
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
        Supports structured commands (JSON) or plain chat.
        """
        import threading
        import json
        from langchain_core.messages import HumanMessage
        from security import KeyringManager
        from brain.memory import get_memory_client
        
        # 1. Parsing Command
        try:
            data = json.loads(text)
            if isinstance(data, dict):
                msg_type = data.get("type")
                
                if msg_type == "save_keys":
                    keys = data.get("data", {})
                    for k, v in keys.items():
                        secret_name = f"ZERO_{k.upper()}_KEY"
                        KeyringManager.set_secret(secret_name, v)
                    NSLog("Zero: Keys saved securely.")
                    return
                
                elif msg_type == "get_cortex_data":
                    self.fetch_cortex_data()
                    return

                elif msg_type == "get_history":
                    self.fetch_history()
                    return

                elif msg_type == "new_chat":
                    self.current_conversation_id = None
                    # Notify UI to clear (optional, UI usually does it immediately)
                    return

                elif msg_type == "load_conversation":
                    cid = data.get("data", {}).get("id")
                    if cid:
                        self.load_conversation(cid)
                    return
                
                elif msg_type == "rename_chat":
                    cid = data.get("data", {}).get("id")
                    title = data.get("data", {}).get("title")
                    if cid and title:
                        db.update_conversation_title(cid, title)
                        self.fetch_history() # Refresh UI
                    return

                elif msg_type == "delete_chat":
                    cid = data.get("data", {}).get("id")
                    if cid:
                        db.delete_conversation(cid)
                        # If current chat is deleted, clear it?
                        if self.current_conversation_id == cid:
                            self.current_conversation_id = None
                            # TODO: Send 'new_chat' signal to UI or handled by fetch_history?
                        self.fetch_history()
                    return
                    
        except json.JSONDecodeError:
            # Not JSON, treat as chat
            pass

        # 2. Handle Chat Message
        def run_graph():
            # A. Ensure Conversation ID
            if not self.current_conversation_id:
                # Create new conversation
                # Use first 30 chars as title for now
                title = text[:30] + "..." if len(text) > 30 else text
                self.current_conversation_id = db.create_conversation(title)
                # Refresh history list in UI so new chat appears
                self.fetch_history()

            # B. Log User Message
            db.add_message(self.current_conversation_id, "user", text)

            # C. Fetch Context
            context = {
                'app': self.monitor.current_app,
                'title': self.monitor.current_title
            }
            
            # D. Prepare Input
            inputs = {
                "messages": [HumanMessage(content=text)],
                "context": context
            }
            
            full_response = ""

            try:
                # E. Stream Output
                for event in self.graph.stream(inputs):
                    # event is typically {'node_name': state_update}
                    for node, values in event.items():
                        if values and "messages" in values:
                            # Get the last message which is the response
                            last_msg = values["messages"][-1]
                            chunk = last_msg.content
                            full_response = chunk 
                            # Stream the content
                            self.webview.stream_response(chunk)
                            
                # F. Log System Response & Memory
                if full_response:
                    db.add_message(self.current_conversation_id, "system", full_response)
                    
                    # Store in Episodic Memory (Mem0)
                    try:
                        mem = get_memory_client()
                        mem.add(f"User: {text}\nSystem: {full_response}", user_id="zero-user")
                    except Exception as e:
                        NSLog(f"Zero: Mem0 Add Error: {e}")

            except Exception as e:
                import traceback
                traceback.print_exc()
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

    def fetch_cortex_data(self):
        """
        Aggregates data for the Cortex Panel (Memories + Tasks).
        """
        import threading
        import json
        from brain.memory import get_memory_client
        
        def run_fetch():
            data = {
                "memories": [],
                "tasks": []
            }
            
            # 1. Fetch Memories
            try:
                mem_client = get_memory_client()
                # memory.get_all() returns list of strings based on my wrapper in memory.py
                raw_mems = mem_client.get_all() 
                # Wrapper returns list[str], so we package it for UI
                data["memories"] = [{"text": m} for m in raw_mems]
            except Exception as e:
                NSLog(f"Zero: Cortex Memory Fetch Error: {e}")
            
            # 2. Fetch Tasks (Mocked for Demo Reliability)
            # In production, we would call github_ops.get_issues(), trello_ops.get_cards()
            # based on stored keys.
            try:
                # User requested to remove hardcode and wait for real integration.
                data["tasks"] = []
            except Exception as e:
                NSLog(f"Zero: Cortex Task Fetch Error: {e}")
            
            # 3. Send to UI
            # Ensure JSON serialization is safe
            try:
                safe_json = json.dumps(data)
                js = f"updateCortex({safe_json})"
                
                from PyObjCTools import AppHelper
                # Call on main thread
                def update_ui():
                    if self.webview:
                        self.webview.evaluateJavaScript_completionHandler_(js, None)
                
                AppHelper.callAfter(update_ui)
            except Exception as e:
                NSLog(f"Zero: Cortex UI Update Error: {e}")
            
        thread = threading.Thread(target=run_fetch)
        thread.start()

    def fetch_history(self):
        """Fetches recent conversations and sends to UI."""
        import json
        from PyObjCTools import AppHelper
        
        try:
            conversations = db.get_recent_conversations()
            # Convert to list of dicts
            data = [dict(c) for c in conversations]
            safe_json = json.dumps(data)
            js = f"updateHistoryList({safe_json})"
            
            def update_ui():
                if self.webview:
                    self.webview.evaluateJavaScript_completionHandler_(js, None)
            
            AppHelper.callAfter(update_ui)
        except Exception as e:
            NSLog(f"Zero: History Fetch Error: {e}")

    def load_conversation(self, conversation_id):
        """Loads messages for a specific conversation."""
        import json
        from PyObjCTools import AppHelper
        
        self.current_conversation_id = conversation_id
        
        try:
            messages = db.get_conversation_messages(conversation_id)
            # Convert to list of dicts
            data = [dict(m) for m in messages]
            safe_json = json.dumps(data)
            js = f"loadChatMessages({safe_json})"
            
            def update_ui():
                if self.webview:
                    self.webview.evaluateJavaScript_completionHandler_(js, None)
            
            AppHelper.callAfter(update_ui)
        except Exception as e:
            NSLog(f"Zero: Conversation Load Error: {e}")

if __name__ == "__main__":
    app = NSApplication.sharedApplication()
    delegate = ZeroAppDelegate.alloc().init()
    app.setDelegate_(delegate)
    
    # Hide from Dock (Ghost Mode)
    # NSApplicationActivationPolicyAccessory = 1
    app.setActivationPolicy_(1)
    
    from PyObjCTools import AppHelper
    AppHelper.runEventLoop()
