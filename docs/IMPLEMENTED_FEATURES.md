# Project ZERO: Implemented Features Status

> [!NOTE]
> This document tracks the functional status of the Zero codebase. It distinguishes between *implemented logic* (code that exists and runs) and *planned architecture* (concepts in the charter).

## 1. Core Application (The "Body")
**Status: ✅ Functional**

*   **Status Bar App (`src/main.py`)**:
    *   Runs as a native macOS menu bar app (icon: "O").
    *   Menu items: "Toggle Zero", "Quit Zero".
    *   **Ghost Mode**: Hidden from Dock (Activation Policy Accessory).
*   **Window Management (`src/gui/window.py`)**:
    *   Custom Floating Panel (borderless, transparent capable).
    *   **Auto-Center**: Summoning centers the window on screen.
    *   **Focus Management**: Hides `NSApplication` when panel is closed to return focus to previous app.
*   **Global Hotkeys (`src/hotkey.py`)**:
    *   `Cmd+Shift+0`: Toggle Thread Window (Summon/Hide).
    *   `Cmd+Shift+9`: Toggle "Ghost Mode" (Visual transparency style).

## 2. User Interface (The "Face")
**Status: ✅ Functional**

*   **Hybrid WebView (`src/gui/webview.py`)**:
    *   Uses system `WKWebView` wrapped in Python/ObjC.
    *   **Transparent Background**: Configured for `clearColor` to support custom UI shapes.
    *   **Bi-directional Bridge**:
        *   Python -> JS: `evaluateJavaScript` (e.g., `updateContext`, `streamResponse`).
        *   JS -> Python: `window.webkit.messageHandlers.zero.postMessage`.
    *   **Streaming Support**: Real-time text streaming from backend to frontend.
*   **Frontend Assets (`src/ui/index.html` + `script.js`)**:
    *   *(Inferred from code references)*: Loads local HTML interface.
    *   Supports `ghost-mode` CSS class toggling.

## 3. Intelligence & Orchestration (The "Brain")
**Status: ✅ Functional**

*   **Graph Orchestrator (`src/orchestrator/graph.py`)**:
    *   **Architecture**: `LangGraph` StateGraph.
    *   **Integration**: Fully transplanted into `src/main.py`.
    *   **Execution Model**: Runs in a background thread to prevent UI blocking.
    *   **Routing**: Logic determines response flow (currently Echo/Router node).
*   **Agent Communication**:
    *   **Context Binding**: `ContextMonitor` data (`current_app`) is passed to the Graph.
    *   **Streaming**: Output is streamed chunk-by-chunk to the WebView.

## 4. Context & Senses (The "Eyes")
**Status: 🚧 Partial**

*   **Context Monitor (`src/context/monitor.py`)**:
    *   **Active App Tracking**: Listens for `NSWorkspaceDidActivateApplicationNotification` to track focused apps.
    *   **Idle Detection**: Monitors System HID events to detect when user steps away (>5 mins).
    *   **Event Loop Integration**: Runs on background thread, updates Main Thread UI via callback.
*   **Limitations**: Currently uses `localizedName` for window titles. Full Accessibility (AX) reading for "Deep Vision" is **planned but not implemented**.

## 5. Persistence (The "Memory")
**Status: ✅ Functional**

*   **SQLite Database (`src/database/db.py`)**:
    *   Local `activity.db` created in `src/database/`.
    *   **Session Tracking**: Logs App Boot time (queried from `sysctl` for accuracy).
    *   **Activity Logging**: Records `app_name`, `window_title`, `duration`, and `is_idle` for every app switch.
