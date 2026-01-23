from pydantic import BaseModel
import re

class SecurityException(Exception):
    """Raised when a security policy is violated."""
    pass

class SecurityAirlock(BaseModel):
    """
    The Security Airlock acts as a firewall between the Agent and the external world.
    It sanitizes outgoing data and validates tool execution requests.
    """
    
    @staticmethod
    def sanitize_outgoing(text: str) -> str:
        """
        Redacts PII (Emails, Phone Numbers) from the text using Regex.
        """
        # Redact Emails
        email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
        text = re.sub(email_pattern, '[REDACTED_EMAIL]', text)
        
        # Redact Phone Numbers (Generic North American style xxx-xxx-xxxx)
        # This is a basic pattern and might need refinement for international numbers
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        text = re.sub(phone_pattern, '[REDACTED_PHONE]', text)
        
        return text

    @staticmethod
    def validate_tool_request(tool_name: str, args: dict):
        """
        Acts as a firewall for tool execution.
        Raises SecurityException for destructive actions without confirmation.
        """
        if tool_name == "calendar" and args.get("action") == "delete":
            if not args.get("user_confirmation"):
                raise SecurityException(
                    f"Blocked destructive action: '{tool_name}.delete'. "
                    "User confirmation required."
                )
        
        # In the future, other tools like 'fs.delete' or 'shell.execute' would go here.
        return True
