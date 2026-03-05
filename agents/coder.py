from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import create_react_agent
from tools.file_tools import read_file, write_file, list_directory, search_code
from tools.memory_tools import read_memory, update_memory


SYSTEM_PROMPT = """You are a specialized coding agent. You read, understand, and write code.

Your capabilities:
- Read files to understand existing code
- List directories to explore project structure
- Search for patterns across a codebase
- Write or modify files to implement changes

Work methodically:
1. First explore/read relevant files to understand the context
2. Make targeted, minimal changes
3. Verify your changes make sense in context
4. Summarize what you did and what files were modified"""


def create_coder_agent(llm: ChatAnthropic):
    """Create the coder ReAct agent with file tools."""
    tools = [read_file, write_file, list_directory, search_code, read_memory, update_memory]
    return create_react_agent(llm, tools, prompt=SYSTEM_PROMPT)
