
import sys
import os
import uuid

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from database import db

def test_chat_actions():
    print("Initializing DB...")
    db.init_db()
    
    # 1. Create a test conversation
    print("Creating test conversation...")
    conv_id = db.create_conversation("Original Title")
    print(f"Created Conversation: {conv_id}")
    
    # Verify it exists
    history = db.get_recent_conversations()
    found = next((c for c in history if c['id'] == conv_id), None)
    if not found:
        print("FAIL: Conversation not found after creation.")
        return
        
    print(f"Verified Title: {found['title']}")
    
    # 2. Rename
    print("Renaming conversation...")
    new_title = "Renamed Title"
    db.update_conversation_title(conv_id, new_title)
    
    # Verify rename
    history = db.get_recent_conversations()
    found = next((c for c in history if c['id'] == conv_id), None)
    if not found or found['title'] != new_title:
        print(f"FAIL: Rename failed. Got '{found['title'] if found else 'None'}', expected '{new_title}'")
    else:
        print("PASS: Rename successful.")
        
    # 3. Add message and then Delete
    print("Adding message...")
    db.add_message(conv_id, "user", "Test message")
    
    print("Deleting conversation...")
    db.delete_conversation(conv_id)
    
    # Verify delete
    history = db.get_recent_conversations()
    found = next((c for c in history if c['id'] == conv_id), None)
    if found:
        print("FAIL: Conversation still exists after delete.")
    else:
        # Verify messages deleted?
        # Accessing private db conn for verification
        import sqlite3
        conn = sqlite3.connect(db.DB_PATH)
        c = conn.cursor()
        c.execute("SELECT count(*) FROM messages WHERE conversation_id = ?", (conv_id,))
        count = c.fetchone()[0]
        conn.close()
        
        if count > 0:
            print(f"FAIL: Messages still exist ({count}).")
        else:
            print("PASS: Delete successful (Conversation and Messages removed).")

if __name__ == "__main__":
    test_chat_actions()
