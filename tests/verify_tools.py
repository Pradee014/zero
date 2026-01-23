import sys
import os
import time

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from tools import ALL_TOOLS
from tools.calendar_ops import calendar_ops
from tools.email_ops import email_ops
from tools.os_ops import get_current_time
from tools.web_ops import get_weather
from security import KeyringManager

def test_tools():
    print("=== Verifying Tools ===")
    
    # 1. Time
    print("\n[Time Tool]")
    print(get_current_time.invoke({}))
    
    # 2. Weather
    print("\n[Weather Tool] (wttr.in)")
    print(get_weather.invoke({"location": "San Francisco"}))
    
    # 3. Keyring
    print("\n[Keyring] Testing Set/Get")
    KeyringManager.set_secret("TEST_KEY", "secret_value")
    val = KeyringManager.get_secret("TEST_KEY")
    if val == "secret_value":
        print("SUCCESS: Keyring Set/Get works.")
        KeyringManager.set_secret("TEST_KEY", "") # Cleanup
    else:
        print(f"FAILURE: Keyring returned '{val}'")

    # 4. Calendar (Requires Permission)
    print("\n[Calendar] Reading Today (Expect Pop-up or Result)")
    try:
        res = calendar_ops.invoke({"action": "read", "date_range": "today"})
        print(f"Result (First 100 chars): {res[:100]}...")
    except Exception as e:
        print(f"Calendar Error: {e}")

    # 5. Email (Requires Permission)
    print("\n[Email] Reading Inbox (Limit 1)")
    try:
        res = email_ops.invoke({"action": "read_inbox", "limit": 1})
        print(f"Result (First 100 chars): {res[:100]}...")
    except Exception as e:
        print(f"Email Error: {e}")
        
    print("\n=== Verification Complete ===")

if __name__ == "__main__":
    test_tools()
