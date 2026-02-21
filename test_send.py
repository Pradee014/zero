import os
import sys

# Ensure src is in path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from src.tools.email_ops import email_ops

def test_send():
    print("Testing direct send email action...")
    try:
        res = email_ops.invoke({
            'action': 'send_email',
            'recipient': 'p.pradeepkumar014@gmail.com', # Assuming you want to test with your own email
            'subject': 'Automated Background Test',
            'body': 'This is a test of the invisible background sending feature.',
            'user_confirmation': True # Simulating the AI properly passing the airlock
        })
        print(f"Result: {res}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_send()
