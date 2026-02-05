import Cocoa
from Cocoa import (
    NSPanel,
    NSWindowStyleMaskNonactivatingPanel,
    NSWindowStyleMaskBorderless,
    NSWindowStyleMaskHUDWindow,
    NSWindowStyleMaskUtilityWindow,
    NSBackingStoreBuffered,
    NSFloatingWindowLevel,
    NSColor,
    NSScreen,
    NSRect
)
import objc

class ZeroPanel(NSPanel):
    def init(self):
        # Calculate center position
        screen = NSScreen.mainScreen()
        screen_rect = screen.frame()
        width = 700
        height = 500
        
        x = (screen_rect.size.width - width) / 2
        y = (screen_rect.size.height - height) / 2
        
        rect = NSRect((x, y), (width, height))
        
        # Style masks
        style_mask = (
            NSWindowStyleMaskBorderless |
            NSWindowStyleMaskNonactivatingPanel 
        )
        
        self = objc.super(ZeroPanel, self).initWithContentRect_styleMask_backing_defer_(
            rect,
            style_mask,
            NSBackingStoreBuffered,
            False
        )
        
        if self:
            self.setLevel_(NSFloatingWindowLevel)
            self.setBackgroundColor_(NSColor.clearColor())
            self.setOpaque_(False)
            self.setHasShadow_(False) # Shadow handled by CSS to fix corner issues
            self.setMovableByWindowBackground_(True)
            self.setBecomesKeyOnlyIfNeeded_(False) # Allow it to become key
            self.setHidesOnDeactivate_(False) # Prevent hiding/transparency on background click
            
        return self

    def canBecomeKeyWindow(self):
        return True

    def performKeyEquivalent_(self, event):
        modifiers = event.modifierFlags()
        
        # Cmd + Opt + Arrows for Moving Window
        if (modifiers & Cocoa.NSEventModifierFlagCommand) and (modifiers & Cocoa.NSEventModifierFlagOption):
            key = event.charactersIgnoringModifiers()
            # Handle Arrows (Special keys)
            # Arrow keys often come as specific unicode or virtual key codes. 
            # charactersIgnoringModifiers for arrows might be empty or specific values on some layouts.
            # Safer to check keyCode or specific selector.
            
            # Key Codes for Arrows (standard):
            # Left: 123, Right: 124, Down: 125, Up: 126
            code = event.keyCode()
            current_frame = self.frame()
            origin = current_frame.origin
            step = 50
            
            moved = False
            if code == 123: # Left
                origin.x -= step
                moved = True
            elif code == 124: # Right
                origin.x += step
                moved = True
            elif code == 126: # Up (Screen coords: Up is +Y)
                origin.y += step
                moved = True
            elif code == 125: # Down (Screen coords: Down is -Y)
                origin.y -= step
                moved = True
            
            if moved:
                self.setFrameOrigin_(origin)
                return True
        
        # Handle Cmd+Q
        if modifiers & Cocoa.NSEventModifierFlagCommand:
            chars = event.charactersIgnoringModifiers()
            if chars and chars.lower() == 'q':
                Cocoa.NSApplication.sharedApplication().terminate_(self)
                return True
                
        return objc.super(ZeroPanel, self).performKeyEquivalent_(event)
