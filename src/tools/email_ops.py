import subprocess
from langchain_core.tools import tool
from typing import Optional, Literal
from pydantic import BaseModel, Field

class EmailInput(BaseModel):
    action: Literal["read_inbox", "draft_email", "send_email"] = Field(..., description="Action: 'read_inbox', 'draft_email', or 'send_email'")
    limit: Optional[int] = Field(5, description="Number of emails to read (default 5)")
    recipient: Optional[str] = Field(None, description="Recipient email address")
    subject: Optional[str] = Field(None, description="Email subject")
    body: Optional[str] = Field(None, description="Email body content")
    sender: Optional[str] = Field(None, description="Optional. The exact email address to send from. If not provided, it falls back to the .env file account.")
    user_confirmation: Optional[bool] = Field(False, description="CRITICAL: Set this to True if the user has EXPLICITLY confirmed they want to send the email.")

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
def email_ops(action: str, limit: int = 5, recipient: str = None, subject: str = None, body: str = None, sender: str = None, user_confirmation: bool = False) -> str:
    """
    Interact with the local macOS Mail app. 
    Can read the inbox, draft new emails (opens the window), or send emails directly (in the background).
    """
    # 0. Global Security Airlock Check
    from security import SecurityAirlock
    SecurityAirlock.validate_tool_request("email_tool", {
        "action": action, 
        "user_confirmation": user_confirmation
    })
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

    elif action == "send_email":
        if not recipient:
            return "Error: recipient required"
            
        subj = subject or "No Subject"
        content = body or ""
        
        # 1. Determine Sender
        import os
        from dotenv import load_dotenv
        load_dotenv()
        env_sender = os.getenv("ZERO_EMAIL_SENDER")
        final_sender = sender or env_sender
        
        # 2. Build AppleScript
        script = f'''
        tell application "Mail"
            -- Create invisibly
            set newMessage to make new outgoing message with properties {{subject:"{subj}", content:"{content}", visible:false}}
            tell newMessage
                make new to recipient at end of to recipients with properties {{address:"{recipient}"}}
        '''
        
        # 3. Add explicit sender if configured
        if final_sender:
            script += f'''
                set sender to "{final_sender}"
            '''
            
        script += '''
                send
            end tell
        end tell
        return "Email queued for sending in the background."
        '''
        result = run_applescript(script)
        return f"Result: {result}"

        
    return "Invalid action"
