# Fullstack Architecture

Zero is a **Hybrid Desktop App**. It combines the system-level access of Python with the rendering capabilities of a Web Browser.

## 1. The Bridge (`UserScriptInjection`)

We do not use HTTP to talk between backend and frontend. We use the **WebKit Message Bridge** for 0ms latency and security.

### Frontend -> Backend
JavaScript sends messages via `window.webkit.messageHandlers`:

```javascript
// script.js
window.webkit.messageHandlers.zero.postMessage({
    type: "query",
    content: "Hello Zero"
});
```

This is intercepted by `ZeroWebView.userContentController_didReceiveScriptMessage_` in `src/gui/webview.py`.

### Backend -> Frontend
Python executes Javascript directly in the view context:

```python
# src/gui/webview.py
def stream_response(self, text):
    js = f"window.receiveStreamChunk('{text}')"
    self.evaluateJavaScript_completionHandler_(js, None)
```

## 2. Frontend Stack

*   **HTML:** `src/ui/index.html` - Semantic structure.
*   **CSS:** `src/ui/style.css` - Custom styling. Use CSS Variables for theming.
    *   *Glassmorphism:* heavily relies on `backdrop-filter: blur()` (though native window transparency handles the main window blur).
*   **JS:** `src/ui/script.js` - Logic for chat rendering, markdown parsing (using `marked` or similar lib), and state management.

## 3. Backend Stack (Python)

*   **PyObjC:** The glue. It wraps Cocoa classes (`NSWindow`, `NSApplication`) as Python objects.
    *   *Loop:* The app runs the native macOS `NSRunLoop`, not a Python `while True` loop. This is critical for event handling.
*   **Dependencies:**
    *   `langchain/langgraph`: AI Logic.
    *   `httpx`: Async networking.
    *   `sqlite3`: Database.

## 4. Threading Model

> [!IMPORTANT]
> **Crash Prevention:** The Main Thread (UI Thread) MUST NOT block.

*   **Main Thread:** Handles UI updates, Key events, Window movement.
*   **Graph Thread:** LLM generation happens here. Output is messaged back to Main Thread for rendering.
*   **Monitor Thread:** `ContextMonitor` runs on a background thread to check active apps without stuttering the UI.
