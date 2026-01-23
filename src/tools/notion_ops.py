from langchain_core.tools import tool
from notion_client import Client
from typing import Optional
import sys
import os

# Add src to path to import security
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from security import KeyringManager

def get_notion_client():
    token = KeyringManager.get_secret("ZERO_NOTION_KEY")
    if not token:
        raise ValueError("Notion API Key not found. Please set it in Settings.")
    return Client(auth=token)

@tool("notion_search")
def search_notion(query: str) -> str:
    """Search for pages in Notion."""
    try:
        notion = get_notion_client()
        response = notion.search(query=query)
        results = response.get("results", [])
        if not results:
            return "No results found."
        
        summary = ""
        for page in results[:5]: # Top 5
            # Identify title
            title = "Untitled"
            props = page.get("properties", {})
            # Title property varies (Name, title, etc)
            # Simple heuristic
            for k, v in props.items():
                if v["type"] == "title":
                    if v["title"]:
                        title = v["title"][0]["plain_text"]
                    break
            
            url = page.get("url")
            summary += f"- [{title}]({url})\n"
        return summary
    except Exception as e:
        return f"Notion Error: {e}"

@tool("notion_create_page")
def create_page(parent_id: str, title: str) -> str:
    """Create a new page in Notion (under a parent page/block)."""
    try:
        notion = get_notion_client()
        # parent_id should be UUID
        response = notion.pages.create(
            parent={"page_id": parent_id},
            properties={
                "title": [
                    {"text": {"content": title}}
                ]
            }
        )
        return f"Page created: {response.get('url')}"
    except Exception as e:
        return f"Notion Error: {e}"
