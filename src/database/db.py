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

    # Conversations table
    c.execute('''CREATE TABLE IF NOT EXISTS conversations (
        id TEXT PRIMARY KEY,
        title TEXT,
        created_at TIMESTAMP,
        updated_at TIMESTAMP
    )''')

    # Messages table
    c.execute('''CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        conversation_id TEXT,
        role TEXT,
        content TEXT,
        created_at TIMESTAMP,
        FOREIGN KEY(conversation_id) REFERENCES conversations(id)
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

# --- Chat History Functions ---

def create_conversation(title=None):
    """Creates a new conversation and returns its ID."""
    import uuid
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    conv_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    
    if not title:
        title = "New Chat"
        
    c.execute("INSERT INTO conversations (id, title, created_at, updated_at) VALUES (?, ?, ?, ?)",
              (conv_id, title, now, now))
    conn.commit()
    conn.close()
    return conv_id



def delete_conversation(conversation_id):
    """Deletes a conversation and its messages."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Delete messages first
    c.execute("DELETE FROM messages WHERE conversation_id = ?", (conversation_id,))
    # Delete conversation
    c.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))
    conn.commit()
    conn.close()

def update_conversation_title(conversation_id, title):
    """Updates the title of a conversation."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute("UPDATE conversations SET title = ?, updated_at = ? WHERE id = ?", 
              (title, now, conversation_id))
    conn.commit()
    conn.close()

def add_message(conversation_id, role, content):
    """Adds a message to a conversation."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.now().isoformat()
    
    # Insert message
    c.execute("INSERT INTO messages (conversation_id, role, content, created_at) VALUES (?, ?, ?, ?)",
              (conversation_id, role, content, now))
              
    # Update conversation timestamp
    c.execute("UPDATE conversations SET updated_at = ? WHERE id = ?", (now, conversation_id))
    
    conn.commit()
    conn.close()

def get_recent_conversations(limit=50):
    """Returns a list of recent conversations."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute("SELECT id, title, updated_at FROM conversations ORDER BY updated_at DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    
    conversations = [dict(row) for row in rows]
    conn.close()
    return conversations

def get_conversation_messages(conversation_id):
    """Returns all messages for a conversation."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute("SELECT role, content, created_at FROM messages WHERE conversation_id = ? ORDER BY id ASC", (conversation_id,))
    rows = c.fetchall()
    
    messages = [dict(row) for row in rows]
    conn.close()
    return messages
