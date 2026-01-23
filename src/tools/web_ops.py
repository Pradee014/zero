import requests
from langchain_core.tools import tool
from typing import Optional

@tool("weather_tool")
def get_weather(location: Optional[str] = None) -> str:
    """
    Get the current weather for a location (or local IP if None).
    Uses wttr.in service.
    """
    # Format 3 is a one-line output: "Paris: ⛅️ +12°C"
    # Format 4 is also good. Let's try format 3 for conciseness or empty for full.
    # The user probably wants a summary.
    # Let's use format=3 by default.
    
    loc_param = location if location else ""
    url = f"https://wttr.in/{loc_param}?format=3"
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.text.strip()
        else:
            return f"Error fetching weather: {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"
