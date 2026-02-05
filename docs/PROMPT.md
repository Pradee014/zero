# Prompt Engineering & Management

Prompts are the source code of the AI. We treat them with the same rigor as Python code.

## 1. System Prompts

The "Soul" of Zero is defined in `src/orchestrator/prompts.py` (suggested location).

**Core Persona:**
> "You are Zero, a hyper-capable macOS assistant. You are concise, precise, and favor code over chatter. You are integrated into the user's system."

**Dynamic Injection:**
We inject real-time context into the system prompt at runtime:

```python
SYSTEM_TEMPLATE = """
You are Zero.
Current Time: {time}
Optimized for: macOS {os_version}

# CONTEXT
App: {current_app}
Window: {window_title}
Clipboard: {clipboard_snippet}

# CAPABILITIES
- You can run terminal commands (ask for permission).
- You can search the web.
"""
```

## 2. Prompt Templates

We use standard LangChain `ChatPromptTemplate` for structured inputs.

### "Chain of Thought" Enforcement
For complex tasks, we wrap prompts to force resoning:
> "Before executing, plan your steps in a <thought> block."

## 3. Prompt Registry (Future)

To support multiple agents, we will move to a YAML-based prompt registry:

```yaml
# prompts/researcher.yaml
task: "Research"
parameters: ["topic", "depth"]
template: |
  You are a relentless researcher.
  Topic: {topic}
  ...
```

## 4. Security in Prompts

**Prompt Injection Defense:**
*   User input is always clearly demarcated:
    `User Query: """ {user_input} """`
*   System instructions are placed *after* user input in some models to prevent override, or we use "System" role strictness.
