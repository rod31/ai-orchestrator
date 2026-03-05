# AI Orchestrator

An agentic coding workflow powered by Claude and LangGraph. Give it a task in plain English and it plans, codes, runs commands, manages git, and researches — autonomously.

## How it works

A **supervisor** routes your task between 6 specialist agents:

| Agent | Does |
|-------|------|
| **planner** | Breaks complex tasks into steps before acting |
| **coder** | Reads and writes code files |
| **executor** | Runs shell commands (tests, installs, builds) |
| **git** | Manages version control (status, commits, branches) |
| **researcher** | Searches the web and reads documentation |
| **workflow_generator** | Creates new agents and workflows |

## Setup

**1. Clone and create a virtual environment**
```bash
git clone https://github.com/YOUR_USERNAME/ai-orchestrator.git
cd ai-orchestrator
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Add your Anthropic API key**
```bash
cp .env.example .env
# Edit .env and set ANTHROPIC_API_KEY=your-key-here
```

## Usage

```bash
# Basic task
python main.py "Add input validation to the login form"

# Target a specific project directory
python main.py --dir ./my-project "Write unit tests for the auth module"

# Use a faster/cheaper model
python main.py --model claude-sonnet-4-6 "Explain what this codebase does"

# Stream output — see which agent is working at each step
python main.py --stream "Refactor the payment module and commit the changes"
```

## Project memory

The orchestrator can remember context about your project across runs. When an agent writes to `.orchestrator/memory.md` in your working directory, that context is automatically loaded on the next run — so it already knows your stack, conventions, and key decisions.

## Programmatic usage

```python
from workflows.coding_workflow import CodingWorkflow

wf = CodingWorkflow(working_directory="./my-project")
result = wf.run("Add a health check endpoint")
print(result)
```

## Requirements

- Python 3.10+
- An [Anthropic API key](https://console.anthropic.com/)
