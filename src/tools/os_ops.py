from langchain_core.tools import tool
from datetime import datetime
import time

@tool("time_tool")
def get_current_time() -> str:
    """
    Get the current local system time and date.
    Returns ISO format and a human readable string.
    """
    now = datetime.now()
    # Get timezone
    tz = time.strftime('%Z')
    
    return f"ISO: {now.isoformat()}\nHuman: {now.strftime('%A, %B %d, %Y %I:%M %p')} {tz}"
