import Cocoa
import WebKit
import os
import json
from Cocoa import NSURL, NSURLRequest, NSObject, NSColor
import objc

# Handler for JS messages
class ZeroScriptHandler(NSObject):
    def initWithWebView_(self, webview):
        self = objc.super(ZeroScriptHandler, self).init()
        self.webview = webview
        return self

    # Protocol: WKScriptMessageHandler
    def userContentController_didReceiveScriptMessage_(self, controller, message):
        if message.name() == "zero":
            body = message.body()
            # Logic to parse body (string, dict, or weird ObjC dict)
            data = None
            if isinstance(body, str):
                try:
                    data = json.loads(body)
                except:
                    data = body # assume raw string
            else:
                # It's likely a PyObjC wrapper (NSFrozenDictionaryM/__NSCFDictionary)
                # We can try to cast to dict, or just treat it as dict-like
                data = body
            
            # If data is a dict-like object (handled by PyObjC bridge)
            # 1. Handle Window Drag
            drag_type = None
            try:
                # specific check because 'get' might not exist on ALL objc objects
                # but usually works for dicts
                drag_type = data.get("type")
            except:
                pass

            if drag_type == "drag":
                # Must happen on next runloop event usually, but performWindowDragWithEvent 
                # needs the CURRENT event.
                app = Cocoa.NSApplication.sharedApplication()
                event = app.currentEvent()
                if event and self.webview.window():
                     self.webview.window().performWindowDragWithEvent_(event)
                return
            

            


            # 2. Legacy/Standard Query Handling
            text = body # Pass raw body if simpler, or extract 'text'
            
            # Delegate to WebView's assigned callback
            if hasattr(self.webview, 'on_query') and self.webview.on_query:
                self.webview.on_query(text)
            else:
                print("Zero: No query handler assigned to WebView")

class ZeroWebView(WebKit.WKWebView):
    def initWithFrame_(self, frame):
        # Configuration
        config = WebKit.WKWebViewConfiguration.alloc().init()
        controller = WebKit.WKUserContentController.alloc().init()
        
        self.handler = ZeroScriptHandler.alloc().initWithWebView_(self)
        controller.addScriptMessageHandler_name_(self.handler, "zero")
        
        config.setUserContentController_(controller)
        
        self = objc.super(ZeroWebView, self).initWithFrame_configuration_(frame, config)
        
        if self:
            self.setValue_forKey_(False, "drawsBackground") # Private-ish key for older WebKit, often needed
            self.setBackgroundColor_(NSColor.clearColor()) # Standard NSView property
            self.setOpaque_(False) # Standard NSView property
            
            self.on_query = None # Callback function(text)
            self.load_local_ui()
            
        return self

    def stream_response(self, text_chunk):
        """
        Stream a chunk of text to the UI.
        """
        # Called from background thread, need to dispatch to main for UI update
        def update_ui():
            safe_text = json.dumps(text_chunk)
            js = f"streamResponse({safe_text})"
            self.evaluateJavaScript_completionHandler_(js, None)
            
        from PyObjCTools import AppHelper
        AppHelper.callAfter(update_ui)

    def on_response_received(self, response_text):
        # Legacy full response
        # Called from background thread, need to dispatch to main for UI update
        def update_ui():
            # Escape text for JS
            # import json (moved to top level)
            safe_text = json.dumps(response_text)
            js = f"receiveResponse({safe_text})"
            self.evaluateJavaScript_completionHandler_(js, None)
            
        from PyObjCTools import AppHelper
        AppHelper.callAfter(update_ui)

    def toggle_ghost_mode(self):
        js = "document.getElementById('app').classList.toggle('ghost-mode')"
        self.evaluateJavaScript_completionHandler_(js, None)

    def send_context_update(self, context_data):
        """
        Sends context update to frontend.
        context_data: dict { 'app': str, 'title': str }
        """
        safe_json = json.dumps(context_data)
        js = f"updateContext({safe_json})"
        
        # Ensure we run on main thread
        from PyObjCTools import AppHelper
        def run_js():
            self.evaluateJavaScript_completionHandler_(js, None)
        AppHelper.callAfter(run_js)

    def load_local_ui(self):
        # Resolve path to ui/index.html
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # src/gui -> src/ui
        ui_path = os.path.join(os.path.dirname(current_dir), 'ui', 'index.html')
        
        if os.path.exists(ui_path):
            url = NSURL.fileURLWithPath_(ui_path)
            request = NSURLRequest.requestWithURL_(url)
            self.loadRequest_(request)
        else:
            print(f"Error: UI file not found at {ui_path}")

    # Disable right-click menu (optional)
    def willOpenMenu_withEvent_(self, menu, event):
        return None
