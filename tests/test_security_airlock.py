import unittest
from src.security import SecurityAirlock, SecurityException

class TestSecurityAirlock(unittest.TestCase):
    
    def test_sanitize_outgoing(self):
        # Mixed content
        input_text = "Contact me at bob@example.com or 555-019-2834 regarding the issue."
        expected_output = "Contact me at [REDACTED_EMAIL] or [REDACTED_PHONE] regarding the issue."
        
        sanitized = SecurityAirlock.sanitize_outgoing(input_text)
        self.assertEqual(sanitized, expected_output)
        
    def test_sanitize_outgoing_no_pii(self):
        input_text = "Just a normal string with no secrets."
        sanitized = SecurityAirlock.sanitize_outgoing(input_text)
        self.assertEqual(sanitized, input_text)

    def test_firewall_block_delete_without_confirmation(self):
        with self.assertRaises(SecurityException) as cm:
            SecurityAirlock.validate_tool_request(
                "calendar", 
                {"action": "delete", "event_id": "123"}
            )
        self.assertIn("Blocked destructive action", str(cm.exception))

    def test_firewall_allow_delete_with_confirmation(self):
        try:
            SecurityAirlock.validate_tool_request(
                "calendar", 
                {"action": "delete", "event_id": "123", "user_confirmation": True}
            )
        except SecurityException:
            self.fail("SecurityException raised despite user_confirmation=True")

    def test_firewall_passthrough_read(self):
        try:
            SecurityAirlock.validate_tool_request(
                "calendar", 
                {"action": "read", "date": "today"}
            )
        except SecurityException:
            self.fail("SecurityException raised for non-destructive action")

if __name__ == '__main__':
    unittest.main()
