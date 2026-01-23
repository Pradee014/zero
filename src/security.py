from pydantic import BaseModel
import re
import keyring

class SecurityException(Exception):
    """Raised when a security policy is violated."""
    pass

class KeyringManager:
    """
    Manages secure access to API keys using the system keychain.
    Service name is 'ZeroAgent'.
    """
    SERVICE_NAME = "ZeroAgent"

    @staticmethod
    def set_secret(key_name: str, secret_value: str):
        if not secret_value:
             # If empty, delete the key if it exists
             try:
                 keyring.delete_password(KeyringManager.SERVICE_NAME, key_name)
             except keyring.errors.PasswordDeleteError:
                 pass # Key didn't exist
        else:
            keyring.set_password(KeyringManager.SERVICE_NAME, key_name, secret_value)

    @staticmethod
    def get_secret(key_name: str) -> str:
        try:
            return keyring.get_password(KeyringManager.SERVICE_NAME, key_name) or ""
        except Exception:
            # Fallback or error handling
            return ""

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
        if not text:
            return ""
            
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
