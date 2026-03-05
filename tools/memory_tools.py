import os
from langchain_core.tools import tool


MEMORY_FILENAME = ".orchestrator/memory.md"


def load_memory(working_directory: str) -> str:
    """
    Load project memory from .orchestrator/memory.md.
    Returns the memory content, or empty string if no memory exists.
    Called at workflow startup, not as an agent tool.
    """
    memory_path = os.path.join(working_directory, MEMORY_FILENAME)
    if not os.path.exists(memory_path):
        return ""
    try:
        with open(memory_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception:
        return ""


@tool
def read_memory(working_directory: str) -> str:
    """Read the current project memory from .orchestrator/memory.md."""
    memory_path = os.path.join(working_directory, MEMORY_FILENAME)
    if not os.path.exists(memory_path):
        return "(no project memory yet)"
    try:
        with open(memory_path, "r", encoding="utf-8") as f:
            return f.read().strip() or "(memory file is empty)"
    except Exception as e:
        return f"Error reading memory: {e}"


@tool
def update_memory(working_directory: str, content: str) -> str:
    """
    Update the project memory file at .orchestrator/memory.md.
    This file persists important context across runs: stack decisions, conventions,
    key file locations, and architectural choices.
    Pass the FULL new content - this overwrites the existing memory.
    Read the current memory first, then write a clean updated version.
    """
    memory_path = os.path.join(working_directory, MEMORY_FILENAME)
    try:
        os.makedirs(os.path.dirname(memory_path), exist_ok=True)
        with open(memory_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Memory updated at {memory_path}"
    except Exception as e:
        return f"Error updating memory: {e}"
