from app.state import AgentState
from app.tools.filesystem import list_dir
from app.tools.search import find_files, read_snippet

MAX_CONTEXT_FILES = 10


def codebase_search(state: AgentState) -> dict:
    repo_path = state["repo_path"]
    components = state.get("likely_components", [])

    relevant_files = find_files(repo_path, components)[:MAX_CONTEXT_FILES]

    # Fall back to top-level listing when search finds nothing
    if not relevant_files:
        relevant_files = [f for f in list_dir(repo_path, max_depth=1) if not f.endswith("/")][
            :MAX_CONTEXT_FILES
        ]

    context_snippets = [f"# {f}\n{read_snippet(f, repo_path)}" for f in relevant_files]

    return {
        "relevant_files": relevant_files,
        "context_snippets": context_snippets,
    }
