import unittest
import os
import time
from database import db

class TestDatabase(unittest.TestCase):
    def setUp(self):
        # Use a temporary test database
        self.test_db_path = "test_activity.db"
        db.DB_PATH = self.test_db_path
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
            
        db.init_db()

    def tearDown(self):
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

    def test_log_activity(self):
        start = time.time()
        end = start + 5.0
        
        db.log_activity("TestApp", "TestTitle", start, end, is_idle=False)
        
        # Verify
        import sqlite3
        conn = sqlite3.connect(self.test_db_path)
        c = conn.cursor()
        c.execute("SELECT * FROM activity_log")
        rows = c.fetchall()
        conn.close()
        
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][1], "TestApp")
        self.assertEqual(rows[0][2], "TestTitle")
        self.assertAlmostEqual(rows[0][5], 5.0, places=1)

if __name__ == '__main__':
    unittest.main()
