# Project ZERO: Overview

**Zero** is a native macOS intelligence layer designed to act as an omnipresent, context-aware "sidekick." Unlike standard chatbots, Zero is deeply integrated into the operating system, allowing it to "see" your active context and "act" on your behalf.

> [!NOTE]
> **Philosophy:** Zero is designed to be "Ghost-like" — invisible when not needed, but instantly available with a keystroke. It prioritizes speed, native integration, and privacy.

## High-Level Architecture

The system is composed of four distinct biological metaphors:

### 1. The Body (Native Core)
*   **Role:** The vessel that lives in the OS.
*   **Implementation:** Python + PyObjC.
*   **Key Features:**
    *   **Menu Bar App:** Runs as a status bar item (`NSStatusBar`).
    *   **Ghost Mode:** Can run as an `NSApplicationActivationPolicyAccessory`, hiding it from the Dock and CMD+TAB switcher.
    *   **Global Hotkeys:** Uses `Quartz` event taps to listen for `Cmd+Shift+0` (summon) and `Cmd+Shift+9` (toggle visibility mode).

### 2. The Face (User Interface)
*   **Role:** The interaction layer for the user.
*   **Implementation:** `WKWebView` hosted in a potentially transparent `NSWindow`.
*   **Key Features:**
    *   **Hybrid Bridge:** A bi-directional JSON bridge allows Python to drive the UI and JS to trigger Python actions.
    *   **Fluid UI:** Built with HTML/CSS/JS, allowing for rich animations, streaming text, and dynamic components that native Cocoa UI makes difficult.
    *   **Transparency:** The window supports `clearColor` backgrounds, allowing for non-rectangular, floating interface designs.

### 3. The Brain (Intelligence & Orchestration)
*   **Role:** The decision maker.
*   **Implementation:** LangGraph (`src/orchestrator/graph.py`).
*   **Key Features:**
    *   **Stateful Reasoning:** Unlike linear chains, the Graph maintains state, allowing for multi-turn conversations and complex task execution.
    *   **Tool Use:** The brain has access to tools (Shell, File System, Browser) via a secure interface.
    *   **Airlock:** All tool execution is gated by a security layer (`src/security.py`) to prevent unauthorized destructive actions.

### 4. The Eyes (Context & Senses)
*   **Role:** Perception of the environment.
*   **Implementation:** `ContextMonitor` (`src/context/monitor.py`).
*   **Key Features:**
    *   **App Focus:** Tracks the currently active `NSRunningApplication`.
    *   **Window Titles:** Reads the title of the frontmost window (e.g., "filename.py - VS Code").
    *   **Idle Detection:** Monitors HID events (Mouse/Keyboard) to detect user presence.
    *   *Planned:* Accessibility API (AX) reading for deep screen content extraction.

## Directory Structure

```text
src/
├── main.py             # Entry point (AppDelegate)
├── gui/                # Window & WebView logic
├── orchestrator/       # LangGraph agents
├── context/            # OS monitoring
├── database/           # SQLite logs
├── ui/                 # Frontend assets (HTML/JS)
└── hotkey.py           # Global keyboard listeners
```
