import requests
from langchain_core.tools import tool
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from security import KeyringManager

def get_trello_creds():
    # Expecting "KEY:TOKEN" format in the secret
    secret = KeyringManager.get_secret("ZERO_TRELLO_KEY")
    if not secret or ":" not in secret:
        raise ValueError("Trello Creds missing or invalid. Use 'KEY:TOKEN' format in Settings.")
    key, token = secret.split(":", 1)
    return key.strip(), token.strip()

@tool("trello_get_boards")
def get_boards() -> str:
    """Get list of Trello boards."""
    try:
        key, token = get_trello_creds()
        url = f"https://api.trello.com/1/members/me/boards?key={key}&token={token}"
        response = requests.get(url)
        if response.status_code == 200:
            boards = response.json()
            summary = ""
            for b in boards:
                summary += f"- {b['name']} (ID: {b['id']})\n"
            return summary
        else:
            return f"Trello Error: {response.status_code} {response.text}"
    except Exception as e:
        return f"Error: {e}"

@tool("trello_add_card")
def add_card(list_id: str, name: str, desc: str = "") -> str:
    """Add a card to a Trello list."""
    try:
        key, token = get_trello_creds()
        url = "https://api.trello.com/1/cards"
        query = {
            'key': key,
            'token': token,
            'idList': list_id,
            'name': name,
            'desc': desc
        }
        response = requests.post(url, params=query)
        if response.status_code == 200:
            data = response.json()
            return f"Card created: {data.get('shortUrl')}"
        else:
            return f"Trello Error: {response.text}"
    except Exception as e:
        return f"Error: {e}"
