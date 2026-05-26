from pathlib import Path

from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from app.config import settings
from app.prompts.templates import IMPLEMENT_SYSTEM
from app.state import AgentState
from app.tools.filesystem import read_file, write_file


class FileUpdate(BaseModel):
    path: str
    content: str


class ImplementationResult(BaseModel):
    files: list[FileUpdate]


def implement(state: AgentState) -> dict:
    repo_path = state["repo_path"]
    files_to_modify = state.get("files_to_modify", [])
    plan = state.get("implementation_plan", [])
    test_results = state.get("test_results", {})
    iteration = state.get("iteration_count", 0)

    file_contents = []
    for rel_path in files_to_modify:
        full = Path(repo_path) / rel_path
        content = read_file(full) if full.exists() else "(new file)"
        file_contents.append(f"### {rel_path}\n```\n{content}\n```")

    failure_context = ""
    if iteration > 0 and test_results:
        failure_context = (
            f"\n\nPrevious attempt failed. Test output:\n"
            f"stdout: {test_results.get('stdout', '')[:2000]}\n"
            f"stderr: {test_results.get('stderr', '')[:2000]}\n"
            f"Failed tests: {test_results.get('failed_tests', [])}"
        )

    user_msg = (
        "Implementation plan:\n" + "\n".join(f"- {s}" for s in plan) + "\n\n"
        "Files to modify:\n" + "\n\n".join(file_contents) + failure_context
    )

    llm = ChatOpenAI(model=settings.model, api_key=settings.openai_api_key)
    structured = llm.with_structured_output(ImplementationResult)

    result: ImplementationResult = structured.invoke(
        [
            {"role": "system", "content": IMPLEMENT_SYSTEM},
            {"role": "user", "content": user_msg},
        ]
    )

    modified: list[str] = []
    for update in result.files:
        full_path = Path(repo_path) / update.path
        write_file(full_path, update.content)
        modified.append(update.path)

    return {
        "modified_files": modified,
        "iteration_count": iteration + 1,
    }
