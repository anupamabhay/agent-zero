import os
import subprocess
import sys
from langchain_core.tools import tool


@tool
def open_in_app(filename: str, app_name: str = None) -> str:
    """Opens a file from the workspace in a specific host application (e.g., 'notepad', 'notepad++', 'obsidian').
    If app_name is not provided, it opens with the system default application.
    This tool works best when the agent is running on the host machine.
    """
    try:
        # Check if we are in Docker
        if os.path.exists("/.dockerenv"):
            return "Error: Cannot open GUI applications directly from inside a Docker container. Please run the agent locally to use this feature."

        # Get the absolute path
        from src.config import settings

        workspace_root = os.path.abspath(settings.workspace_root)
        file_path = os.path.join(workspace_root, filename)

        if not os.path.exists(file_path):
            return f"Error: File '{filename}' not found in workspace."

        if sys.platform == "win32":
            if app_name:
                # Use 'start' to avoid blocking and allow existing instances
                subprocess.Popen(
                    ["cmd", "/c", "start", "", app_name, file_path], shell=True
                )
            else:
                os.startfile(file_path)
            return f"Successfully opened '{filename}' on the host."
        elif sys.platform == "darwin":  # macOS
            cmd = ["open"]
            if app_name:
                cmd.extend(["-a", app_name])
            cmd.append(file_path)
            subprocess.Popen(cmd)
            return f"Successfully opened '{filename}'."
        else:  # Linux
            cmd = ["xdg-open", file_path]
            subprocess.Popen(cmd)
            return f"Successfully opened '{filename}'."

    except Exception as e:
        return f"Error opening file: {str(e)}"
