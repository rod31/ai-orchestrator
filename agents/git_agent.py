from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import create_react_agent
from tools.git_tools import (
    git_status, git_diff, git_log,
    git_add, git_commit, git_create_branch, git_checkout,
)


SYSTEM_PROMPT = """You are a specialized git agent. You manage version control for the project.

Your capabilities:
- Check repository status and diffs
- View commit history
- Stage files and create commits
- Create and switch branches

Guidelines:
- Always check git_status before staging or committing
- Write clear, descriptive commit messages (imperative mood: "Add X", "Fix Y")
- Never force-push or delete branches without explicit instruction
- When branching, use descriptive names like feature/add-auth or fix/null-pointer
- Summarize what version control actions were taken"""


def create_git_agent(llm: ChatAnthropic):
    """Create the git ReAct agent with git tools."""
    tools = [git_status, git_diff, git_log, git_add, git_commit, git_create_branch, git_checkout]
    return create_react_agent(llm, tools, prompt=SYSTEM_PROMPT)
