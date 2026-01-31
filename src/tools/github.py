import os
import shutil
import zipfile
from pathlib import Path
from langchain_core.tools import tool
from git import Repo
from src.config import settings
from src.tools.filesystem import _get_safe_path
from typing import List, Optional


@tool
def ingest_external_source(source_url_or_path: str, target_folder: str) -> str:
    """Clones a public GitHub repo or extracts a local .zip file into the workspace.
    - If URL starts with http/https and ends with .git, it clones the repo.
    - If it ends with .zip, it extracts it.
    """
    try:
        target_path = _get_safe_path(target_folder)
        if target_path.exists():
            return f"Error: Target folder '{target_folder}' already exists. Please choose a new one."

        target_path.mkdir(parents=True, exist_ok=True)

        if source_url_or_path.endswith(".git") and source_url_or_path.startswith(
            "http"
        ):
            Repo.clone_from(source_url_or_path, target_path)
            return f"Successfully cloned repository into {target_folder}"

        elif source_url_or_path.endswith(".zip"):
            zip_path = Path(source_url_or_path)
            if not zip_path.exists():
                return f"Error: Zip file not found at {source_url_or_path}"

            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(target_path)
            return f"Successfully extracted zip into {target_folder}"

        else:
            return "Error: Unsupported source type. Use a .git URL or a path to a .zip file."

    except Exception as e:
        return f"Error ingesting source: {str(e)}"


@tool
def get_repo_history(directory: str = ".", count: int = 10) -> str:
    """Retrieves the latest commit history from a git repository.
    Used for generating accurate scrum reports and tracking updates.
    """
    try:
        repo_path = _get_safe_path(directory)
        repo = Repo(repo_path)

        if repo.bare:
            return "Error: Could not find a valid git repository at this location."

        commits = list(repo.iter_commits(max_count=count))
        history = []
        for commit in commits:
            date = commit.authored_datetime.strftime("%Y-%m-%d %H:%M")
            history.append(f"[{date}] {commit.author.name}: {commit.summary}")

        return f"Recent Activity in {directory}:\n" + "\n".join(history)
    except Exception as e:
        return f"Error reading git history: {str(e)}"


@tool
def get_file_diffs(directory: str = ".") -> str:
    """Shows the uncommitted changes in the repository to see what is currently being worked on."""
    try:
        repo_path = _get_safe_path(directory)
        repo = Repo(repo_path)
        diff = repo.git.diff()
        return (
            f"Uncommitted changes in {directory}:\n{diff[:2000]}..."
            if diff
            else "No uncommitted changes."
        )
    except Exception as e:
        return f"Error reading diffs: {str(e)}"
