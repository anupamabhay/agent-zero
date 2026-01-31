from langchain_core.tools import tool
from duckduckgo_search import DDGS
import httpx
from bs4 import BeautifulSoup
from typing import Optional


@tool
def search_web(query: str, max_results: int = 5) -> str:
    """Searches the web for the given query using DuckDuckGo."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
            if not results:
                return f"No results found for '{query}'."

            output = [f"Search results for '{query}':"]
            for i, res in enumerate(results, 1):
                output.append(
                    f"{i}. {res['title']}\n   URL: {res['href']}\n   Snippet: {res['body']}"
                )

            return "\n\n".join(output)
    except Exception as e:
        return f"Error searching the web: {str(e)}"


@tool
def scrape_website(url: str) -> str:
    """Scrapes the text content from a given URL."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        with httpx.Client(
            headers=headers, follow_redirects=True, timeout=10.0
        ) as client:
            response = client.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Remove script and style elements
            for script_or_style in soup(["script", "style"]):
                script_or_style.decompose()

            # Get text and clean it up
            text = soup.get_text(separator="\n")
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = "\n".join(chunk for chunk in chunks if chunk)

            # Limit text length to avoid token issues (arbitrary limit)
            return text[:10000]
    except Exception as e:
        return f"Error scraping the website: {str(e)}"
