import os
from langchain_core.tools import tool


@tool
def generate_agent_template(name: str, description: str, tool_names: list[str]) -> str:
    """
    Generate a new LangGraph ReAct agent Python file.
    Args:
        name: snake_case name for the agent (e.g. 'summarizer')
        description: what this agent does (used in its system prompt)
        tool_names: list of tool names from the tools/ module this agent should use
    Returns the path of the created file.
    """
    class_name = "".join(w.capitalize() for w in name.split("_"))
    tools_import = ", ".join(tool_names) if tool_names else ""
    tools_list = ", ".join(tool_names) if tool_names else ""

    content = f'''from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import create_react_agent
{"from tools import " + tools_import if tools_import else ""}


SYSTEM_PROMPT = """You are a specialized agent. {description}

Work methodically and use your tools to accomplish the task. When done, summarize what you did."""


def create_{name}_agent(llm: ChatAnthropic):
    """Create the {name} ReAct agent."""
    tools = [{tools_list}]
    return create_react_agent(llm, tools, prompt=SYSTEM_PROMPT)
'''

    agents_dir = os.path.join(os.path.dirname(__file__), "..", "agents")
    os.makedirs(agents_dir, exist_ok=True)
    filepath = os.path.join(agents_dir, f"{name}.py")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    return f"Created agent at agents/{name}.py"


@tool
def generate_workflow_template(name: str, agent_names: list[str]) -> str:
    """
    Generate a new LangGraph supervisor workflow Python file.
    Args:
        name: snake_case name for the workflow (e.g. 'review_workflow')
        agent_names: list of agent names (snake_case) to include as nodes
    Returns the path of the created file.
    """
    imports = "\n".join(
        f"from agents.{a} import create_{a}_agent" for a in agent_names
    )
    agent_init = "\n        ".join(
        f'"{a}": create_{a}_agent(self.llm),' for a in agent_names
    )
    members_list = str(agent_names)

    content = f'''from typing import Annotated, Literal
from typing_extensions import TypedDict
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from pydantic import BaseModel
{imports}


MEMBERS = {members_list}
OPTIONS = MEMBERS + ["FINISH"]


class RouteDecision(BaseModel):
    next: Literal[{", ".join(repr(a) for a in agent_names)}, "FINISH"]


class WorkflowState(TypedDict):
    messages: Annotated[list, add_messages]
    next: str
    working_directory: str


class {name.title().replace("_", "")}:
    def __init__(self, working_directory: str = ".", model: str = "claude-opus-4-6"):
        self.working_directory = working_directory
        self.llm = ChatAnthropic(model=model)
        self.agents = {{
            {agent_init}
        }}
        self.graph = self._build_graph()

    def _supervisor_node(self, state: WorkflowState):
        supervisor_llm = self.llm.with_structured_output(RouteDecision)
        system = f"""You are a supervisor orchestrating these agents: {", ".join(MEMBERS)}.
Given the conversation, decide which agent should act next, or FINISH if the task is complete."""
        messages = [{{"role": "system", "content": system}}] + state["messages"]
        decision = supervisor_llm.invoke(messages)
        return {{"next": decision.next}}

    def _agent_node(self, agent_name: str):
        def node(state: WorkflowState):
            agent = self.agents[agent_name]
            result = agent.invoke({{
                "messages": state["messages"],
                "working_directory": state["working_directory"],
            }})
            last = result["messages"][-1]
            return {{"messages": [HumanMessage(content=last.content, name=agent_name)]}}
        return node

    def _build_graph(self):
        graph = StateGraph(WorkflowState)
        graph.add_node("supervisor", self._supervisor_node)
        for name in MEMBERS:
            graph.add_node(name, self._agent_node(name))

        graph.add_edge(START, "supervisor")
        for name in MEMBERS:
            graph.add_edge(name, "supervisor")
        graph.add_conditional_edges(
            "supervisor",
            lambda s: s["next"],
            {{**{{name: name for name in MEMBERS}}, "FINISH": END}},
        )
        return graph.compile()

    def run(self, task: str) -> str:
        result = self.graph.invoke({{
            "messages": [HumanMessage(content=task)],
            "next": "",
            "working_directory": self.working_directory,
        }})
        return result["messages"][-1].content
'''

    workflows_dir = os.path.join(os.path.dirname(__file__), "..", "workflows")
    os.makedirs(workflows_dir, exist_ok=True)
    filepath = os.path.join(workflows_dir, f"{name}.py")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    return f"Created workflow at workflows/{name}.py"
