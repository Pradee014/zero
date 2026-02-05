# Memory & Persistence

Zero possesses both **Short-term Working Memory** (Context) and **Long-term Episodic Memory** (Database).

## 1. Local Database

*   **Path:** `src/database/activity.db` (SQLite)
*   **Manager:** `src/database/db.py`

### Schema

#### `sessions`
Tracks application runs (boot to quit).
| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | INTEGER PK | Auto-inc ID |
| `start_time` | TEXT | ISO Timestamp of boot |
| `end_time` | TEXT | ISO Timestamp of shutdown (optional) |

#### `activity_log`
Tracks user context switches.
| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | INTEGER PK | Auto-inc ID |
| `session_id` | INT FK | Link to session |
| `timestamp` | TEXT | When the switch occurred |
| `app_name` | TEXT | e.g., "VS Code" |
| `window_title` | TEXT | e.g., "graph.py" |
| `duration` | REAL | Time spent in previous state (seconds) |
| `is_idle` | BOOLEAN | True if user was away |

## 2. Working Memory (Context)

Working memory is ephemeral and lives in the `ContextMonitor`.

*   **Current State:** `monitor.current_app`, `monitor.current_title`
*   **Usage:** Injected into every LLM prompt as a system message:
    > "User is currently using {app} working on {title}."

## 3. Future Memory Capabilities

### Semantic Search (Vector Store)
*   **Goal:** Allow users to ask "What was I working on last Tuesday?"
*   **Implementation:**
    1.  Embed `window_title` and OCR snapshots (future).
    2.  Store in a local vector DB (e.g., Chroma or LanceDB).
    3.  RAG system retrieves relevant past activities.

### User Preferences (KeyValue Store)
*   **Goal:** Remember user-specific instructions.
*   **Structure:** JSON blob or simple KV table.
*   **Example:** "Always use Python 3.12", "Don't suggest `sudo`".
