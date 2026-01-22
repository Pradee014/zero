# Project ZERO: The Autonomous Personal Enterprise

## 1. Executive Summary
**ZERO** is not just a chatbot; it is a **Multi-Agent Orchestration System** designed to function as a dedicated startup team for the Founder (User).

Built on a philosophy of **"Zero Friction, Zero Latency, Zero Trust,"** the system runs locally on macOS, leveraging a hybrid architecture of native "Senses" (for vision/hearing) and containerized "Brains" (for logic). The goal is to provide enterprise-grade assistance—coding, research, operations, and coaching—without compromising security or privacy.

---

## 2. Core Philosophy
* **Founder-Centric:** The user is not an "admin" but the **Founder**. The agents act as proactive employees, not passive tools.
* **Tunnel Vision Security:** Agents only see what they strictly need. "Dev-0" sees code but not finance; "Web-0" sees the internet but not local passwords.
* **Local-First:** The primary interface and orchestration logic run on the local machine (Mac Studio/MacBook), ensuring "No Air to Breathe" security for sensitive routing.
* **Model Agnostic:** The system uses **Ollama Cloud** (initially) for intelligence but is architected to swap models (Local Llama, OpenAI, Anthropic) via configuration, not code changes.

---

## 3. Organizational Chart (Agent Roster)
The system is structured as a corporate C-Suite. Each agent is a specialized entity with distinct permissions, tools, and personality.

### 🤖 1. Zero Prime (The Chief of Staff)
**"The Gatekeeper"**
* **Role:** The interface between the Founder and the Machine.
* **Clearance:** **Level 5 (Root)**.
* **Location:** Native macOS System Tray / Floating HUD.
* **Responsibilities:**
    * **Intent Recognition:** Deciphers the Founder's request (e.g., "Fix this" vs. "Research this") and delegates to the correct department.
    * **Security Enforcement:** Sanitizes inputs to ensure sensitive data (API keys, passwords) is never sent to lower-clearance agents like Web-0.
    * **Memory Management:** Maintains the "Master Context"—the Founder’s goals, current projects, and preferences.
    * **Feedback Loop:** Aggregates reports from other agents and presents a single, concise summary to the Founder.

### 💻 2. Dev-0 (The CTO / Lead Engineer)
**"The Builder"**
* **Role:** Technical execution and software development.
* **Clearance:** **Level 4 (Local/Code)**.
* **Access:** VS Code (Deep Vision), Terminal, Docker, GitHub, Local Files.
* **Responsibilities:**
    * **Deep Vision:** Uses macOS Accessibility API (AX) to read active code in the IDE without screenshots.
    * **Implementation:** Writes, refactors, and debugs code across multiple languages (Python, Rust, JS).
    * **DevOps:** Manages git operations (commit, push, PR), runs test suites, and handles deployments.
    * **Tooling:** Interacts with Antigravity, Cursor, and database servers.

### 🗂️ 3. Ops-0 (The COO / Operations Manager)
**"The Organizer"**
* **Role:** Knowledge management and logistics.
* **Clearance:** **Level 3 (Private Data)**.
* **Access:** Notion, Obsidian, Google Calendar, Gmail, Slack/Communication Tools.
* **Responsibilities:**
    * **Second Brain Management:** Connects dots between scattered data (e.g., linking a Calendar meeting to an Obsidian project note).
    * **Communications:** Drafts emails in the Founder's voice, summarizes long threads, and manages inbox triage.
    * **Scheduling:** Negotiates meeting times and organizes the daily agenda.
    * **Documentation:** Updates project roadmaps and status reports automatically.

### 🌐 4. Scout-0 (The Head of Research)
**"The Explorer"**
* **Role:** External information gathering and intelligence.
* **Clearance:** **Level 1 (Public Internet)**.
* **Access:** Web Browser (Chrome/Arc), Search APIs, Public Documentation.
* **Responsibilities:**
    * **Market Intelligence:** Monitors competitors, news, and industry trends.
    * **Technical Research:** Finds documentation, StackOverflow solutions, or library references for Dev-0.
    * **QA Testing:** Validates public-facing deployments (e.g., "Go to our website and check if the signup button works").
    * **Sandboxing:** Operates in a strict isolation layer to prevent web-based attacks from reaching the core system.

### 🎓 5. Coach-0 (The VP of Performance)
**"The Mentor"**
* **Role:** Skill acquisition and Founder development.
* **Clearance:** **Level 2 (Analysis)**.
* **Access:** Read-only analysis of interactions, Training Modules.
* **Responsibilities:**
    * **Active Coaching:** Runs roleplay simulations (e.g., "Simulate a tough VC negotiation").
    * **Passive Critique:** analyzing communication style (e.g., "That email sounded defensive; here is a more diplomatic version").
    * **Skill Trees:** Tracks the Founder's progress in specific domains (Communication, Leadership, Technical Architecture) and suggests learning resources.

---

## 4. Technical Architecture

### The "Senses" (Native Layer)
* **Language:** Python 3.12 (Native)
* **Tools:** `pyobjc`, `rumps`, `Quartz`.
* **Function:** Handles the "Ghost Overlay" UI, Global Hotkeys (`Cmd+Shift+0`), and Window/Voice input capture. It is the "Body" of the system.

### The "Brain" (Orchestration Layer)
* **Framework:** PydanticAI / LangGraph.
* **Model Provider:** Ollama Cloud (Configurable to Local/OpenAI).
* **Protocol:** **MCP (Model Context Protocol)**. Used to standardize connections between agents and tools (Notion, GitHub, Postgres) without brittle custom code.

### The "Vision" (Context Layer)
* **Protocol:** **Tiered Access**.
    1.  **Tier 1 (Metadata):** Zero Prime reads Window Titles instantly (Low cost).
    2.  **Tier 2 (Deep Vision):** Dev-0 reads Text Content via Accessibility API (High fidelity).
    3.  **Tier 3 (Optical):** Fallback to Computer Vision (Screenshots) only when AX fails.

---

## 5. Security Protocol (Clearance Levels)
Project ZERO enforces a **Least Privilege** model.

| Level | Designation | Description | Example Data |
| :--- | :--- | :--- | :--- |
| **L5** | **ROOT** | Full system oversight. | Master Intent, Routing Rules. |
| **L4** | **SENSITIVE** | High-value local assets. | SSH Keys, Source Code, Env Vars. |
| **L3** | **PRIVATE** | Personal data/communications. | Emails, Calendar, Notes. |
| **L2** | **INTERNAL** | Analysis data only. | Performance Logs, Chat History. |
| **L1** | **PUBLIC** | Untrusted external data. | Web Pages, Search Results. |

* **Rule:** Information flows **UP**, commands flow **DOWN**.
* **Rule:** L1 Agents (Scout) can NEVER access L4 Data (Keys).

---

## 6. Future Roadmap
* **Phase 1:** Native Chat Overlay + Zero Prime (Orchestrator).
* **Phase 2:** Dev-0 Integration (Deep Vision for VS Code).
* **Phase 3:** Ops-0 Integration (Notion/Calendar MCP).
* **Phase 4:** Voice Mode (Local STT/TTS).
* **Phase 5:** Full Autonomous "Swarm" Mode.