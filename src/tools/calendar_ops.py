import subprocess
import datetime
from langchain_core.tools import tool
from typing import Optional, Literal
from pydantic import BaseModel, Field

class CalendarInput(BaseModel):
    action: Literal["read", "draft_event"] = Field(..., description="Action to perform: 'read' or 'draft_event'")
    date_range: Optional[str] = Field(None, description="For 'read': 'today', 'tomorrow', or 'YYYY-MM-DD,YYYY-MM-DD'")
    event_details: Optional[dict] = Field(None, description="For 'draft_event': {'summary': '...', 'start_time': 'YYYY-MM-DD HH:MM', 'end_time': '...'}")

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

@tool("calendar_tool", args_schema=CalendarInput)
def calendar_ops(action: str, date_range: str = None, event_details: dict = None) -> str:
    """
    Interact with the local macOS Calendar app. 
    Can read events for a date range or draft new events.
    """
    if action == "read":
        # Parse date range
        start_date = datetime.date.today()
        end_date = start_date
        
        if date_range == "today":
            pass
        elif date_range == "tomorrow":
            start_date += datetime.timedelta(days=1)
            end_date = start_date
        elif date_range and "," in date_range:
            try:
                s, e = date_range.split(",")
                start_date = datetime.datetime.strptime(s.strip(), "%Y-%m-%d").date()
                end_date = datetime.datetime.strptime(e.strip(), "%Y-%m-%d").date()
            except ValueError:
                return "Error: Invalid date format. Use YYYY-MM-DD,YYYY-MM-DD"
        
        # AppleScript to Read
        # Note: 'events whose start date >= date ...' is complex in raw AppleScript.
        # We'll fetch all events for the calendars and filter in Python or simplified AS.
        # Efficient approach: ask Calendar for specific range.
        
        s_str = start_date.strftime("%m/%d/%Y") # AppleScript often likes M/D/Y
        e_str = (end_date + datetime.timedelta(days=1)).strftime("%m/%d/%Y")
        
        script = f'''
        tell application "Calendar"
            set output to ""
            set searchStart to date "{s_str}"
            set searchEnd to date "{e_str}"
            
            repeat with oneCal in calendars
                tell oneCal
                    set foundEvents to (every event whose start date is greater than or equal to searchStart and start date is less than searchEnd)
                    repeat with oneEvent in foundEvents
                        set evtTitle to summary of oneEvent
                        set evtStart to start date of oneEvent
                        set evtEnd to end date of oneEvent
                        set evtLoc to location of oneEvent
                        
                        set output to output & "Event: " & evtTitle & " | Start: " & evtStart & " | End: " & evtEnd & " | Loc: " & evtLoc & "\\n"
                    end repeat
                tell oneCal
            end repeat
            return output
        end tell
        '''
        
        # Correction: AS nested tell blocks can be tricky.
        # Simplified loop:
        script = f'''
        set output to ""
        set startDate to date "{s_str}"
        set endDate to date "{e_str}"
        
        tell application "Calendar"
            set allCalendars to calendars
            repeat with aCalendar in allCalendars
                set calendarEvents to (events of aCalendar whose start date is greater than or equal to startDate and start date is less than endDate)
                repeat with anEvent in calendarEvents
                    set evtTitle to summary of anEvent
                    set evtStart to start date of anEvent
                    set evtEnd to end date of anEvent
                    try
                        set evtLoc to location of anEvent
                    on error
                        set evtLoc to "None"
                    end try
                    
                    set output to output & "- [" & (name of aCalendar) & "] " & evtTitle & " (" & evtStart & " to " & evtEnd & ") Loc: " & evtLoc & "\\n"
                end repeat
            end repeat
        end tell
        return output
        '''
        return run_applescript(script)

    elif action == "draft_event":
        if not event_details:
            return "Error: event_details required for draft_event"
        
        summary = event_details.get("summary", "New Event")
        start_str = event_details.get("start_time") # Expect 'YYYY-MM-DD HH:MM'
        end_str = event_details.get("end_time")     # Optional
        
        if not start_str:
            return "Error: start_time required"

        try:
            dt_start = datetime.datetime.strptime(start_str, "%Y-%m-%d %H:%M")
            if end_str:
                dt_end = datetime.datetime.strptime(end_str, "%Y-%m-%d %H:%M")
            else:
                dt_end = dt_start + datetime.timedelta(hours=1)
                
            s_as = dt_start.strftime("%m/%d/%Y %I:%M %p")
            e_as = dt_end.strftime("%m/%d/%Y %I:%M %p")
            
            script = f'''
            tell application "Calendar"
                tell calendar "Calendar"
                    make new event at end with properties {{summary:"{summary}", start date:date "{s_as}", end date:date "{e_as}"}}
                end tell
            end tell
            return "Event drafted successfully."
            '''
            # Note: "Calendar" is the default calendar name often, but might fail if user renamed it.
            # Safer to use 'default calendar' if possible, or just first one.
            
            script = f'''
            tell application "Calendar"
                tell first calendar
                    make new event at end with properties {{summary:"{summary}", start date:date "{s_as}", end date:date "{e_as}"}}
                end tell
            end tell
            return "Event created in first calendar."
            '''
            return run_applescript(script)
            
        except ValueError:
            return "Error: Invalid time format. Use YYYY-MM-DD HH:MM"

    return "Invalid action"
