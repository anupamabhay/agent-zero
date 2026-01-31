import os
from pathlib import Path
from langchain_core.tools import tool
from src.tools.filesystem import _get_safe_path
from typing import List


@tool
def explore_project(directory: str = ".", ignore_dirs: List[str] = None) -> str:
    """Recursively lists all files in a project directory to help understand the structure.
    Useful for generating project updates or scrum reports.
    """
    if ignore_dirs is None:
        ignore_dirs = [
            ".git",
            "__pycache__",
            "node_modules",
            "venv",
            ".venv",
            "dist",
            "build",
        ]

    try:
        root_path = _get_safe_path(directory)
        tree = []

        for root, dirs, files in os.walk(root_path):
            # Filter ignored directories
            dirs[:] = [d for d in dirs if d not in ignore_dirs]

            relative_root = os.path.relpath(root, root_path)
            if relative_root == ".":
                level = 0
            else:
                level = relative_root.count(os.sep) + 1

            indent = "  " * level
            tree.append(f"{indent}{os.path.basename(root)}/")

            sub_indent = "  " * (level + 1)
            for f in files:
                tree.append(f"{sub_indent}{f}")

        return "Project Structure:\n" + "\n".join(tree)
    except Exception as e:
        return f"Error exploring project: {str(e)}"


@tool
def generate_scrum_report(context: str) -> str:
    """Analyzes provided context (like recent changes or project structure)
    and generates a professional Scrum/Demo update report.
    """
    # This tool primarily relies on the Agent's reasoning,
    # but we can provide a structured template.
    template = """
## Scrum/Progress Update
**Date:** {date}

### 1. Accomplishments (What was done?)
{accomplishments}

### 2. Current Focus (What is being worked on?)
{focus}

### 3. Blockers/Risks
{blockers}

### 4. Next Steps
{next_steps}
    """
    return "Please provide the accomplishments, focus, blockers, and next steps to fill the report."
