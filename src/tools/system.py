import subprocess
from langchain_core.tools import tool
from src.config import settings
import os


@tool
def execute_command(command: str, timeout: int = 30) -> str:
    """Executes a shell command securely and returns the output (stdout and stderr).
    The command is executed in the workspace directory.
    """
    try:
        # Resolve the workspace root to an absolute path
        workspace_root = os.path.abspath(settings.workspace_root)

        # Ensure the workspace directory exists
        if not os.path.exists(workspace_root):
            os.makedirs(workspace_root)

        # Execute the command
        result = subprocess.run(
            command,
            shell=True,
            cwd=workspace_root,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        output = []
        if result.stdout:
            output.append(f"STDOUT:\n{result.stdout}")
        if result.stderr:
            output.append(f"STDERR:\n{result.stderr}")

        if not output:
            return "Command executed successfully with no output."

        return "\n".join(output)
    except subprocess.TimeoutExpired:
        return f"Error: Command timed out after {timeout} seconds."
    except Exception as e:
        return f"Error executing command: {str(e)}"
