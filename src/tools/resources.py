import json
import os
from langchain_core.tools import tool
from src.config import settings
from src.tools.web import scrape_website
import datetime

RESOURCES_FILE = "resources_kb.json"


def _get_resources_path():
    return os.path.join(settings.workspace_root, RESOURCES_FILE)


def _load_resources():
    path = _get_resources_path()
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []


def _save_resources(resources):
    path = _get_resources_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(resources, f, indent=4)


@tool
def add_resource(
    url: str, category: str = "Uncategorized", manual_summary: str = None
) -> str:
    """Adds a link/resource to the knowledge base, automatically scrapes a summary if not provided,
    and sorts it by category.
    """
    resources = _load_resources()

    summary = manual_summary
    if not summary:
        # Attempt to auto-summarize by scraping the first 500 chars
        content = scrape_website.invoke({"url": url})
        summary = (
            content[:500].replace("\n", " ") + "..." if len(content) > 500 else content
        )

    new_entry = {
        "url": url,
        "category": category,
        "summary": summary,
        "date_added": datetime.datetime.now().isoformat(),
    }

    resources.append(new_entry)
    _save_resources(resources)

    return f"Successfully added resource to '{category}': {url}"


@tool
def list_resources(category: str = None) -> str:
    """Lists stored resources, optionally filtered by category."""
    resources = _load_resources()
    if not resources:
        return "No resources found."

    if category:
        resources = [r for r in resources if r["category"].lower() == category.lower()]
        if not resources:
            return f"No resources found in category '{category}'."

    output = []
    for r in resources:
        output.append(
            f"[{r['category']}] {r['url']}\n   Summary: {r['summary']}\n   Added: {r['date_added']}"
        )

    return "\n\n".join(output)
