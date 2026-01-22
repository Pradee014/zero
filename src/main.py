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

# Load env variables from .env file
load_dotenv()

class ZeroAppDelegate(NSObject):
    def applicationDidFinishLaunching_(self, notification):
        NSLog("Zero: Launching...")
        
        # 1. Setup Status Bar
        self.status_item = NSStatusBar.systemStatusBar().statusItemWithLength_(NSVariableStatusItemLength)
        self.status_item.button().setTitle_("Z")
        
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
        NSLog("Zero: Ready.")

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

if __name__ == "__main__":
    app = NSApplication.sharedApplication()
    delegate = ZeroAppDelegate.alloc().init()
    app.setDelegate_(delegate)
    
    # Hide from Dock (Ghost Mode)
    # NSApplicationActivationPolicyAccessory = 1
    app.setActivationPolicy_(1)
    
    from PyObjCTools import AppHelper
    AppHelper.runEventLoop()
