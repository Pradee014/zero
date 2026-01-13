import Cocoa
import WebKit
import os
from Cocoa import NSURL, NSURLRequest, NSObject, NSColor
import objc
from network.client import ZeroBrain

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
            # body should be a dict or string
            # Assuming body is dict {type: 'query', text: '...'} or just text
            text = body
            # Call Brain
            if self.webview.brain:
                self.webview.brain.query(text, self.webview.on_response_received)

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
            
            self.brain = ZeroBrain() # Initialize Brain
            self.load_local_ui()
            
        return self

    def on_response_received(self, response_text):
        # Called from background thread, need to dispatch to main for UI update
        def update_ui():
            # Escape text for JS
            import json
            safe_text = json.dumps(response_text)
            js = f"receiveResponse({safe_text})"
            self.evaluateJavaScript_completionHandler_(js, None)
            
        from PyObjCTools import AppHelper
        AppHelper.callAfter(update_ui)

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
