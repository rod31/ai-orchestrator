import subprocess
from langchain_core.tools import tool


def _run_git(args: list[str], cwd: str) -> str:
    """Internal helper - run a git command and return combined output."""
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=30,
        )
        output = result.stdout
        if result.stderr:
            output += result.stderr
        if result.returncode != 0:
            output += f"\n[exit code: {result.returncode}]"
        return output.strip() or "(no output)"
    except subprocess.TimeoutExpired:
        return "Error: git command timed out"
    except FileNotFoundError:
        return "Error: git not found in PATH"
    except Exception as e:
        return f"Error running git: {e}"


@tool
def git_status(cwd: str) -> str:
    """Show the working tree status for the git repo at cwd."""
    return _run_git(["status"], cwd)


@tool
def git_diff(cwd: str, file: str = "") -> str:
    """Show diffs relative to the last commit. Optionally pass a specific file path."""
    args = ["diff", "HEAD"]
    if file:
        args.append(file)
    return _run_git(args, cwd)


@tool
def git_log(cwd: str, n: int = 10) -> str:
    """Show the last n commits in a compact one-line format."""
    return _run_git(["log", "--oneline", f"-{n}"], cwd)


@tool
def git_add(cwd: str, files: str) -> str:
    """Stage files for commit. Pass a space-separated list of file paths, or '.' for all."""
    file_list = files.split()
    return _run_git(["add"] + file_list, cwd)


@tool
def git_commit(cwd: str, message: str) -> str:
    """Commit staged changes with the given message."""
    return _run_git(["commit", "-m", message], cwd)


@tool
def git_create_branch(cwd: str, branch_name: str) -> str:
    """Create a new branch and check it out."""
    return _run_git(["checkout", "-b", branch_name], cwd)


@tool
def git_checkout(cwd: str, branch: str) -> str:
    """Checkout an existing branch."""
    return _run_git(["checkout", branch], cwd)
