import os
from pathlib import Path
from langchain_core.tools import tool
from src.config import settings

def _get_safe_path(filename: str) -> Path:
    """Helper: Enforces sandbox security."""
    safe_root = Path(settings.workspace_root).resolve()
    target_path = (safe_root / filename).resolve()

    if not str(target_path).startswith(str(safe_root)):
        raise ValueError("Security Violation: Attempted access outside of workspace root.")
    return target_path

@tool
def write_file(filename: str, content: str) -> str:
    """Writes content to a file. Overwrites if exists."""
    try:
        path = _get_safe_path(filename)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return f"Successfully wrote to {filename}"
    except Exception as e:
        return f"Failed to write to {filename}: {str(e)}"

@tool
def read_file(filename: str) -> str:
    """Reads the content of a file."""
    try:
        path = _get_safe_path(filename)
        if not path.exists():
            return f"File {filename} does not exist."
        return path.read_text(encoding="utf-8")
    except Exception as e:
        return f"Failed to read {filename}: {str(e)}"
    
@tool
def list_files(directory: str = ".") -> str:
    """Lists files in the given directory (default: root)."""    
    try:
        path = _get_safe_path(directory)
        if not path.is_dir():
            return f"{directory} is not a valid directory."
        
        files = [p.name for p in path.iterdir()]
        return f"Contents of {directory}: {', '.join(files)}"
    except Exception as e:
        return f"Failed to list files in {directory}: {str(e)}"