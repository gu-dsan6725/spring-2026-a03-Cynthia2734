import subprocess
import logging

logger = logging.getLogger(__name__)
CODEBASE_PATH = "../mcp-gateway-registry"

def run_bash(command: str, cwd: str = CODEBASE_PATH, max_chars: int = 8000) -> str:
    """
    Execute a bash command inside the codebase directory and return the output.

    Args:
        command:   The shell command to run
        cwd:       Working directory (defaults to codebase root)
        max_chars: Truncate output if it exceeds this length to avoid
                   overwhelming the LLM context window

    Returns:
        Command stdout as a string, truncated if too long
    """
    logger.info(f"Running bash: {command}")
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=30
        )
        output = result.stdout
        if not output and result.stderr:
            output = result.stderr
        if len(output) > max_chars:
            output = output[:max_chars] + f"\n... [truncated - {len(output)} total chars]"
        return output.strip()
    except subprocess.TimeoutExpired:
        return "Error: Command timed out after 30 seconds."
    except Exception as e:
        return f"Error running command: {e}"