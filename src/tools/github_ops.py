from langchain_core.tools import tool
from github import Github
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from security import KeyringManager

def get_github_client():
    token = KeyringManager.get_secret("ZERO_GITHUB_KEY")
    if not token:
        raise ValueError("GitHub Token missing. Please set it in Settings.")
    return Github(token)

@tool("github_get_issues")
def get_issues(repo_name: str, state: str = "open") -> str:
    """Get issues from a GitHub repo (e.g., 'owner/repo')."""
    try:
        g = get_github_client()
        repo = g.get_repo(repo_name)
        issues = repo.get_issues(state=state)
        
        summary = ""
        count = 0
        for issue in issues:
            if count >= 5: break
            summary += f"#{issue.number} {issue.title} (by {issue.user.login})\n"
            count += 1
        return summary if summary else "No issues found."
    except Exception as e:
        return f"GitHub Error: {e}"

@tool("github_create_issue")
def create_issue(repo_name: str, title: str, body: str = "") -> str:
    """Create an issue in a GitHub repo."""
    try:
        g = get_github_client()
        repo = g.get_repo(repo_name)
        issue = repo.create_issue(title=title, body=body)
        return f"Issue created: {issue.html_url}"
    except Exception as e:
        return f"GitHub Error: {e}"
