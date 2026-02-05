# Context Awareness (The Eyes)

"Context" is what differentiates Zero from a standard web chatbot. It knows what you are doing.

## 1. Application Monitoring

**File:** `src/context/monitor.py`

*   **Mechanism:** Uses `NSWorkspace` notifications.
    *   `NSWorkspaceDidActivateApplicationNotification`: Fired when app focus changes.
*   **Data Captured:**
    *   `localizedName`: "Google Chrome"
    *   `bundleIdentifier`: "com.google.Chrome"

## 2. Window Title Extraction

Getting the window title is harder than it looks due to privacy sandbox (Apple Sandbox).

*   **Method:** AppleScript / Quartz Window Services.
    *   We query the `kCGWindowListOptionOnScreenOnly` to find the window belonging to the active PID.
*   **Permissions:** Requires **Screen Recording Permission** on macOS to read titles of other windows.

## 3. Deep Vision (Planned)

To read the *content* of the screen (e.g., the code inside VS Code, or the email body in Mail), we need to use the **Accessibility API (AXUIElement)**.

### AX Implementation Plan
1.  Get `AXApplication` object for the active PID.
2.  Get `AXFocusedUIElement`.
3.  Walk the tree to find `kAXValueAttribute` (the text content).
4.  **Privacy:** This requires "Accessibility" permission in System Settings.

## 4. Idle Detection

*   **Goal:** Know if the user is present.
*   **Method:** monitor `CGEventSourceSecondsSinceLastEventType`.
*   **Usage:**
    *   If idle > 5 mins -> Pause heavy background tasks.
    *   If idle > 15 mins -> Log "Away" in `activity.db`.
