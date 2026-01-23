import threading
import time
import Cocoa
import Quartz
import objc
from Cocoa import NSWorkspace, NSWorkspaceDidActivateApplicationNotification, NSObject
from PyObjCTools import AppHelper
from database.db import log_activity

class ContextMonitor(NSObject):
    def initWithCallback_(self, callback):
        self = objc.super(ContextMonitor, self).init()
        if self:
            self.workspace = NSWorkspace.sharedWorkspace()
            self.callback = callback
            
            # State
            self.current_app = "Unknown"
            self.current_title = ""
            self.start_time = time.time()
            self.is_running = False
            
            # Idle Config
            self.IDLE_THRESHOLD = 300
            self.idle_check_interval = 60
            self.was_idle = False
        return self
        
    def start(self):
        self.is_running = True
        
        # Register for App Switching Notifications
        notification_center = self.workspace.notificationCenter()
        notification_center.addObserver_selector_name_object_(
            self,
            "appActivated:",
            NSWorkspaceDidActivateApplicationNotification,
            None
        )
        
        # Initial Context
        self.update_context()
        
        # Start Idle Thread
        self.idle_thread = threading.Thread(target=self._idle_loop, daemon=True)
        self.idle_thread.start()
        print("Zero: Context Monitor Started (Event-Driven)")

    def appActivated_(self, notification):
        """Called by macOS when active app changes."""
        self._commit_current_activity()
        self.update_context()

    def update_context(self):
        """Fetches current app info and updates state."""
        front_app = self.workspace.frontmostApplication()
        if front_app:
            new_app = front_app.localizedName()
            # Title access is tricky without Accessibility, using App Name as fallback
            # In a real build, we'd use AXUIElement to get window title
            new_title = new_app 
            
            self.current_app = new_app
            self.current_title = new_title
            self.start_time = time.time()
            
            # Reset idle state when app switches (user is clearly active)
            self.was_idle = False
            
            # Notify UI
            if self.callback:
                self.callback({
                    "app": self.current_app,
                    "title": self.current_title
                })

    def _commit_current_activity(self):
        """Logs the session that just finished."""
        end_time = time.time()
        if self.current_app:
            # If we were idle, we log it as Idle time? 
            # Simplified: limit duration to reasonable active time if it was idle?
            # For now, just log exactly what happened.
            # If was_idle is True, we might want to tag it.
            
            log_activity(
                self.current_app, 
                self.current_title, 
                self.start_time, 
                end_time,
                is_idle=self.was_idle
            )

    def _idle_loop(self):
        """Background thread to check for idle (no mouse/keyboard)."""
        while self.is_running:
            idle_seconds = Quartz.CGEventSourceSecondsSinceLastEventType(
                Quartz.kCGEventSourceStateHIDSystemState, 
                Quartz.kCGAnyInputEventType
            )
            
            if idle_seconds > self.IDLE_THRESHOLD and not self.was_idle:
                print(f"Zero: User is Idle ({idle_seconds}s). Pausing active log.")
                # Commit the active time before idling
                self._commit_current_activity()
                
                # Start an "Idle" session
                self.current_app = "Idle"
                self.current_title = "Away from keyboard"
                self.start_time = time.time()
                self.was_idle = True
                
                if self.callback:
                    self.callback({
                        "app": "Idle",
                        "title": "Away"
                    })
                    
            elif idle_seconds < 10 and self.was_idle:
                # User returned
                print("Zero: User returned.")
                self._commit_current_activity() # Commit the idle block
                
                # We need to re-fetch the actual app because we might still be in VS Code
                self.update_context()
                
            time.sleep(self.idle_check_interval)
