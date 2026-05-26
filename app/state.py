from typing import TypedDict


class AgentState(TypedDict):
    task: str
    repo_path: str
    relevant_files: list[str]
    context_snippets: list[str]
    goal: str
    likely_components: list[str]
    risk_level: str
    requires_tests: bool
    implementation_plan: list[str]
    files_to_modify: list[str]
    modified_files: list[str]
    test_results: dict
    evaluation: dict
    iteration_count: int
    final_summary: str
