# Research Capabilities

The **Research Agent** is a specialized mode where Zero autonomously gathers information to answer complex queries.

## 1. Workflow

1.  **Decomposition:** Break the user query into sub-questions.
    *   *Query:* "Comparison of M3 Max vs M4 Pro for ML workflows"
    *   *Sub-q 1:* "Apple M3 Max ML benchmarks"
    *   *Sub-q 2:* "Apple M4 Pro specs and ML performance"
    *   *Sub-q 3:* "Release date and pricing differences"

2.  **Execution (Web Search):**
    *   Uses `Tavily` or `Google Search API`.
    *   Iterative loop: Search -> Scrape Results -> Analyze -> Decide if more search is needed.

3.  **Synthesis:**
    *   Compiles findings into a report.
    *   Cites sources (URLs).

## 2. Tools

### `browser_search`
*   **Args:** `query` (str)
*   **Returns:** List of {title, url, snippet}.

### `read_url`
*   **Args:** `url` (str)
*   **Returns:** Markdown content of the page.
    *   *Implementation:* Uses `readability` or `BeautifulSoup` to strip nav/ads.

## 3. Deep Research (Plan)

For "Deep Research" (requests that take minutes, not seconds):
*   **Background Thread:** The research runs effectively detached from the chat loop.
*   **Progress Reporting:** The agent sends "Status Events" to the UI ("Reading Article 1/5...", "Analyzing Data...") so the user knows it's working.
*   **Artifact Generation:** The final output is saved as a Markdown Artifact in the chat history, not just a text bubble.
