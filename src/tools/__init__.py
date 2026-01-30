from .calendar_ops import calendar_ops
from .email_ops import email_ops
from .os_ops import get_current_time
from .web_ops import get_weather
from .notion_ops import search_notion, create_page
from .trello_ops import get_boards, add_card
from .github_ops import get_issues, create_issue

ALL_TOOLS = [
    calendar_ops,
    email_ops,
    get_current_time,
    get_weather,
    search_notion,
    create_page,
    get_boards,
    add_card,
    get_issues,
    create_issue
]

# Core Tools for Ops-0 (COO)
OPS_TOOLS = [
    calendar_ops,
    email_ops,
    get_current_time,
    search_notion,
    create_page,
    get_boards,
    add_card
]

# Core Tools for Dev-0 (CTO)
DEV_TOOLS = [
    get_issues,
    create_issue,
    get_current_time
]
