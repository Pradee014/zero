import subprocess
from langchain_core.tools import tool
from typing import Optional, Literal
from pydantic import BaseModel, Field

class EmailInput(BaseModel):
    action: Literal["read_inbox", "draft_email"] = Field(..., description="Action: 'read_inbox' or 'draft_email'")
    limit: Optional[int] = Field(5, description="Number of emails to read (default 5)")
    recipient: Optional[str] = Field(None, description="Recipient email address")
    subject: Optional[str] = Field(None, description="Email subject")
    body: Optional[str] = Field(None, description="Email body content")

def run_applescript(script: str) -> str:
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"AppleScript Error: {e.stderr}"

@tool("email_tool", args_schema=EmailInput)
def email_ops(action: str, limit: int = 5, recipient: str = None, subject: str = None, body: str = None) -> str:
    """
    Interact with the local macOS Mail app. 
    Can read the inbox or draft new emails (opens the window).
    """
    if action == "read_inbox":
        script = f'''
        tell application "Mail"
            set output to ""
            set unreadCount to unread count of inbox
            if unreadCount is 0 then
                return "No unread messages."
            end if
            
            set msgList to (messages of inbox whose read status is false)
            
            -- Limit loop
            set loopCount to {limit}
            if (count of msgList) < loopCount then
                set loopCount to (count of msgList)
            end if
            
            repeat with i from 1 to loopCount
                set msg to item i of msgList
                set msgSubject to subject of msg
                set msgSender to sender of msg
                set msgDate to date received of msg
                -- extracting content is slow and might be huge, skipping for summary
                set output to output & i & ". From: " & msgSender & " | Subj: " & msgSubject & " | Date: " & msgDate & "\\n"
            end repeat
            return output
        end tell
        '''
        return run_applescript(script)

    elif action == "draft_email":
        if not recipient:
            return "Error: recipient required"
        
        subj = subject or "No Subject"
        content = body or ""
        
        script = f'''
        tell application "Mail"
            set newMessage to make new outgoing message with properties {{subject:"{subj}", content:"{content}", visible:true}}
            tell newMessage
                make new to recipient at end of to recipients with properties {{address:"{recipient}"}}
            end tell
            activate
        end tell
        return "Draft email opened."
        '''
        return run_applescript(script)
        
    return "Invalid action"
