import unittest
import sys
import os
import shutil

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from database import db

class TestChatHistory(unittest.TestCase):
    def setUp(self):
        # Use a temporary DB for testing
        self.original_db_path = db.DB_PATH
        db.DB_PATH = self.original_db_path + ".test"
        if os.path.exists(db.DB_PATH):
            os.remove(db.DB_PATH)
        db.init_db()

    def tearDown(self):
        if os.path.exists(db.DB_PATH):
            os.remove(db.DB_PATH)
        db.DB_PATH = self.original_db_path

    def test_create_conversation(self):
        cid = db.create_conversation("Test Chat")
        self.assertIsNotNone(cid)
        
        convs = db.get_recent_conversations()
        self.assertEqual(len(convs), 1)
        self.assertEqual(convs[0]['title'], "Test Chat")
        self.assertEqual(convs[0]['id'], cid)

    def test_add_messages(self):
        cid = db.create_conversation("Message Test")
        
        db.add_message(cid, "user", "Hello")
        db.add_message(cid, "system", "Hi there")
        
        msgs = db.get_conversation_messages(cid)
        self.assertEqual(len(msgs), 2)
        self.assertEqual(msgs[0]['role'], "user")
        self.assertEqual(msgs[0]['content'], "Hello")
        self.assertEqual(msgs[1]['role'], "system")
        self.assertEqual(msgs[1]['content'], "Hi there")

    def test_update_title(self):
        cid = db.create_conversation("Old Title")
        db.update_conversation_title(cid, "New Title")
        
        convs = db.get_recent_conversations()
        self.assertEqual(convs[0]['title'], "New Title")

if __name__ == '__main__':
    unittest.main()
