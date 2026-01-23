import sqlite3
import os
import time
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "activity.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Sessions table (Boot/Login times)
    c.execute('''CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        boot_time TIMESTAMP,
        login_time TIMESTAMP,
        logout_time TIMESTAMP
    )''')
    
    # Activity Log table (App switching events)
    c.execute('''CREATE TABLE IF NOT EXISTS activity_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        app_name TEXT,
        window_title TEXT,
        start_time TIMESTAMP,
        end_time TIMESTAMP,
        duration_seconds REAL,
        is_idle BOOLEAN DEFAULT 0
    )''')
    
    conn.commit()
    conn.close()

def log_session_start(boot_time_iso):
    """Logs a new session start (App Launch)."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    login_time = datetime.now().isoformat()
    c.execute("INSERT INTO sessions (boot_time, login_time) VALUES (?, ?)", (boot_time_iso, login_time))
    conn.commit()
    conn.close()

def log_activity(app_name, window_title, start_time, end_time, is_idle=False):
    """
    Logs a completed activity block.
    start_time and end_time should be float timestamps (time.time()).
    """
    duration = end_time - start_time
    
    # Ignore negligible durations (< 0.5s) to reduce noise from accidental clicks
    if duration < 0.5:
        return

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''INSERT INTO activity_log 
                 (app_name, window_title, start_time, end_time, duration_seconds, is_idle) 
                 VALUES (?, ?, ?, ?, ?, ?)''', 
              (app_name, window_title, start_time, end_time, duration, is_idle))
    conn.commit()
    conn.close()
