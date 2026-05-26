import argparse
import os

from app.config import settings

if settings.langsmith_api_key:
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = settings.langsmith_api_key
    os.environ["LANGCHAIN_PROJECT"] = "coding-assistant"


def main() -> None:
    parser = argparse.ArgumentParser(description="Local agentic coding assistant")
    parser.add_argument("--repo", required=True, help="Path to the target repository")
    parser.add_argument("--task", required=True, help="Natural language task description")
    args = parser.parse_args()

    from app.graph import build_graph

    graph = build_graph()

    initial_state = {
        "task": args.task,
        "repo_path": args.repo,
        "relevant_files": [],
        "context_snippets": [],
        "goal": "",
        "likely_components": [],
        "risk_level": "low",
        "requires_tests": True,
        "implementation_plan": [],
        "files_to_modify": [],
        "modified_files": [],
        "test_results": {},
        "evaluation": {},
        "iteration_count": 0,
        "final_summary": "",
    }

    print(f"Starting agent on repo: {args.repo}")
    print(f"Task: {args.task}\n")

    final_summary = ""

    for step in graph.stream(initial_state):
        node_name = next(iter(step))
        node_state = step[node_name]
        print(f"[{node_name}] done")

        if node_name == "understand":
            print(f"  goal: {node_state.get('goal')}")
            print(f"  risk: {node_state.get('risk_level')}")
        elif node_name == "codebase_search":
            print(f"  files found: {node_state.get('relevant_files', [])}")
        elif node_name == "planner":
            for s in node_state.get("implementation_plan", []):
                print(f"  - {s}")
        elif node_name == "implement":
            print(f"  modified: {node_state.get('modified_files', [])}")
        elif node_name == "test_runner":
            tr = node_state.get("test_results", {})
            print(f"  success: {tr.get('success')}  failed: {tr.get('failed_tests', [])}")
        elif node_name == "evaluate":
            ev = node_state.get("evaluation", {})
            print(f"  status: {ev.get('status')}  reason: {ev.get('reason')}")
            final_summary = node_state.get("final_summary", "")

    print("\n--- SUMMARY ---")
    print(final_summary)


if __name__ == "__main__":
    main()
