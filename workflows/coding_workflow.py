import os
from typing import Annotated, Literal
from typing_extensions import TypedDict
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from pydantic import BaseModel

from agents.coder import create_coder_agent
from agents.executor import create_executor_agent
from agents.workflow_generator import create_workflow_generator_agent
from agents.planner import create_planner_agent
from agents.git_agent import create_git_agent
from agents.researcher import create_researcher_agent
from tools.memory_tools import load_memory

load_dotenv()

MEMBERS = ["planner", "coder", "executor", "git", "researcher", "workflow_generator"]


class RouteDecision(BaseModel):
    next: Literal["planner", "coder", "executor", "git", "researcher", "workflow_generator", "FINISH"]
    reasoning: str


class WorkflowState(TypedDict):
    messages: Annotated[list, add_messages]
    next: str
    working_directory: str


SUPERVISOR_PROMPT = """You are a supervisor orchestrating a coding workflow with these specialist agents:

- **planner**: breaks complex tasks into numbered steps. Use FIRST for multi-step or ambiguous tasks.
- **coder**: reads, understands, and writes code files. Use for: exploring codebases, reading files, writing/editing code.
- **executor**: runs shell commands. Use for: running tests, installing packages, executing builds, linters.
- **git**: manages version control. Use for: status checks, diffs, staging, commits, branching.
- **researcher**: searches the web and fetches URLs. Use for: finding docs, packages, solutions.
- **workflow_generator**: creates new LangGraph agents and workflows. Use for: generating new agent/workflow templates.

Routing guidelines:
- For complex or multi-step tasks, route to planner FIRST
- For simple, clear tasks (e.g. "run the tests"), skip planner and route directly
- Return FINISH only when the task is fully complete

Always explain your routing reasoning briefly."""


class CodingWorkflow:
    """
    A LangGraph-based agentic workflow for coding projects.

    Usage:
        from ai_orchestrator import CodingWorkflow

        wf = CodingWorkflow(working_directory="./my-project")
        result = wf.run("Add unit tests for the auth module")
        print(result)
    """

    def __init__(
        self,
        working_directory: str = ".",
        model: str = "claude-sonnet-4-6",
        api_key: str | None = None,
    ):
        self.working_directory = os.path.abspath(working_directory)
        self.llm = ChatAnthropic(
            model=model,
            api_key=api_key or os.getenv("ANTHROPIC_API_KEY"),
        )
        self._memory = load_memory(self.working_directory)
        self._agents = {
            "planner": create_planner_agent(self.llm),
            "coder": create_coder_agent(self.llm),
            "executor": create_executor_agent(self.llm),
            "git": create_git_agent(self.llm),
            "researcher": create_researcher_agent(self.llm),
            "workflow_generator": create_workflow_generator_agent(self.llm),
        }
        self.graph = self._build_graph()

    def _supervisor_node(self, state: WorkflowState) -> dict:
        supervisor_llm = self.llm.with_structured_output(RouteDecision)
        prompt = SUPERVISOR_PROMPT
        if self._memory:
            prompt += f"\n\n## Project Memory\n{self._memory}"
        messages = [{"role": "system", "content": prompt}] + state["messages"]
        decision = supervisor_llm.invoke(messages)
        return {"next": decision.next}

    def _agent_node(self, agent_name: str):
        def node(state: WorkflowState) -> dict:
            agent = self._agents[agent_name]
            result = agent.invoke({
                "messages": state["messages"],
            })
            last_msg = result["messages"][-1]
            return {
                "messages": [HumanMessage(content=last_msg.content, name=agent_name)]
            }
        return node

    def _route(self, state: WorkflowState) -> str:
        return state["next"]

    def _build_graph(self) -> StateGraph:
        graph = StateGraph(WorkflowState)

        graph.add_node("supervisor", self._supervisor_node)
        for name in MEMBERS:
            graph.add_node(name, self._agent_node(name))

        graph.add_edge(START, "supervisor")
        for name in MEMBERS:
            graph.add_edge(name, "supervisor")

        graph.add_conditional_edges(
            "supervisor",
            self._route,
            {**{name: name for name in MEMBERS}, "FINISH": END},
        )

        return graph.compile()

    def run(self, task: str) -> str:
        """Run the coding workflow on a task. Returns the final response as a string."""
        result = self.graph.invoke({
            "messages": [HumanMessage(content=f"Working directory: {self.working_directory}\n\nTask: {task}")],
            "next": "",
            "working_directory": self.working_directory,
        })
        return result["messages"][-1].content

    def stream(self, task: str) -> None:
        """Stream the workflow, printing agent steps as they complete."""
        for chunk in self.graph.stream(
            {
                "messages": [HumanMessage(content=f"Working directory: {self.working_directory}\n\nTask: {task}")],
                "next": "",
                "working_directory": self.working_directory,
            },
            stream_mode="updates",
        ):
            for node_name, node_output in chunk.items():
                if node_name == "supervisor":
                    print(f"[supervisor] -> {node_output.get('next', '?')}")
                else:
                    msgs = node_output.get("messages", [])
                    if msgs:
                        print(f"\n[{node_name}]")
                        print(msgs[-1].content)
                        print("-" * 60)
