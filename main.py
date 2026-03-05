import argparse
import os
from dotenv import load_dotenv

load_dotenv()

from workflows.coding_workflow import CodingWorkflow


def main():
    parser = argparse.ArgumentParser(
        description="AI Orchestrator - Run agentic coding workflows",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python main.py "Add unit tests for auth module"
  python main.py --dir ./my-project "Refactor the payment module"
  python main.py --model claude-sonnet-4-6 "Quick task"
  python main.py --stream "Show me progress as it runs"
""",
    )
    parser.add_argument("task", help="The task to perform")
    parser.add_argument(
        "--dir",
        default=".",
        metavar="DIRECTORY",
        help="Working directory for the workflow (default: current directory)",
    )
    parser.add_argument(
        "--model",
        default="claude-opus-4-6",
        metavar="MODEL",
        help="Anthropic model to use (default: claude-opus-4-6)",
    )
    parser.add_argument(
        "--stream",
        action="store_true",
        help="Stream output, showing which agent is active at each step",
    )

    args = parser.parse_args()

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not set. Create a .env file or export the variable.")
        raise SystemExit(1)

    wf = CodingWorkflow(
        working_directory=args.dir,
        model=args.model,
        api_key=api_key,
    )

    if args.stream:
        print(f"Working directory: {wf.working_directory}")
        print("-" * 60)
        wf.stream(args.task)
    else:
        result = wf.run(args.task)
        print(result)


if __name__ == "__main__":
    main()
