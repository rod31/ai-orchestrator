import requests
from langchain_core.tools import tool


@tool
def web_search(query: str, max_results: int = 5) -> str:
    """
    Search the web using DuckDuckGo. Returns titles, URLs, and snippets.
    Use for finding documentation, Stack Overflow answers, package info, etc.
    """
    try:
        from ddgs import DDGS
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append(f"Title: {r['title']}\nURL: {r['href']}\nSnippet: {r['body']}\n")
        if not results:
            return f"No results found for: {query}"
        return "\n---\n".join(results)
    except ImportError:
        return "Error: duckduckgo-search package not installed. Run: pip install duckduckgo-search"
    except Exception as e:
        return f"Error searching: {e}"


@tool
def fetch_url(url: str) -> str:
    """
    Fetch a URL and return its text content (HTML stripped to readable text).
    Use for reading documentation pages, GitHub READMEs, articles, etc.
    Truncates to 8000 characters to avoid overwhelming context.
    """
    try:
        from bs4 import BeautifulSoup
        headers = {"User-Agent": "Mozilla/5.0 (compatible; ai-orchestrator/1.0)"}
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        text = soup.get_text(separator="\n", strip=True)
        lines = [l for l in text.splitlines() if l.strip()]
        text = "\n".join(lines)
        if len(text) > 8000:
            text = text[:8000] + "\n...[truncated]"
        return text
    except ImportError:
        return "Error: beautifulsoup4 not installed. Run: pip install beautifulsoup4"
    except requests.exceptions.Timeout:
        return f"Error: request timed out fetching {url}"
    except requests.exceptions.HTTPError as e:
        return f"Error: HTTP {e.response.status_code} for {url}"
    except Exception as e:
        return f"Error fetching URL: {e}"
