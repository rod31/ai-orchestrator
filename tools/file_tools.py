import os
import fnmatch
from langchain_core.tools import tool


@tool
def read_file(path: str) -> str:
    """Read the contents of a file. Returns the file contents as a string."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: File not found: {path}"
    except Exception as e:
        return f"Error reading file: {e}"


@tool
def write_file(path: str, content: str) -> str:
    """Create or overwrite a file with the given content. Creates parent directories if needed."""
    try:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote {len(content)} characters to {path}"
    except Exception as e:
        return f"Error writing file: {e}"


@tool
def list_directory(path: str = ".") -> str:
    """List files and directories at the given path recursively (excludes common noise like __pycache__, .git, venv)."""
    EXCLUDE = {".git", "__pycache__", "venv", ".venv", "node_modules", ".mypy_cache", ".pytest_cache"}
    lines = []
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in EXCLUDE]
        rel_root = os.path.relpath(root, path)
        prefix = "" if rel_root == "." else rel_root + "/"
        for f in sorted(files):
            lines.append(prefix + f)
        for d in sorted(dirs):
            lines.append(prefix + d + "/")
    return "\n".join(lines) if lines else "(empty directory)"


@tool
def search_code(directory: str, pattern: str) -> str:
    """Search for a text pattern across all files in a directory. Returns matching lines with file paths and line numbers."""
    EXCLUDE = {".git", "__pycache__", "venv", ".venv", "node_modules"}
    results = []
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in EXCLUDE]
        for fname in files:
            fpath = os.path.join(root, fname)
            try:
                with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                    for i, line in enumerate(f, 1):
                        if pattern.lower() in line.lower():
                            rel = os.path.relpath(fpath, directory)
                            results.append(f"{rel}:{i}: {line.rstrip()}")
            except Exception:
                continue
    if not results:
        return f"No matches found for '{pattern}' in {directory}"
    return "\n".join(results[:200])  # cap at 200 results
