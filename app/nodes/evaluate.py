from typing import Literal

from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from app.config import settings
from app.prompts.templates import EVALUATE_SYSTEM
from app.state import AgentState


class Evaluation(BaseModel):
    status: Literal["success", "retry", "failed"]
    reason: str
    final_summary: str


def evaluate(state: AgentState) -> dict:
    test_results = state.get("test_results", {})
    iteration = state.get("iteration_count", 0)

    # Short-circuit: tests passed
    if test_results.get("success"):
        return {
            "evaluation": {"status": "success", "reason": "All tests passed"},
            "final_summary": (
                f"Task completed successfully in {iteration} iteration(s).\n"
                f"Modified files: {', '.join(state.get('modified_files', []))}"
            ),
        }

    # Short-circuit: iteration limit
    if iteration >= settings.max_iterations:
        return {
            "evaluation": {
                "status": "failed",
                "reason": f"Reached max iterations ({settings.max_iterations})",
            },
            "final_summary": (
                f"Task failed after {iteration} iteration(s).\n"
                f"Last test output:\n{test_results.get('stdout', '')[:1000]}"
            ),
        }

    llm = ChatOpenAI(model=settings.model, api_key=settings.openai_api_key)
    structured = llm.with_structured_output(Evaluation)

    user_msg = (
        f"Iteration: {iteration}/{settings.max_iterations}\n"
        f"Test success: {test_results.get('success')}\n"
        f"Failed tests: {test_results.get('failed_tests', [])}\n"
        f"stdout:\n{test_results.get('stdout', '')[:2000]}\n"
        f"stderr:\n{test_results.get('stderr', '')[:1000]}"
    )

    result: Evaluation = structured.invoke(
        [
            {"role": "system", "content": EVALUATE_SYSTEM},
            {"role": "user", "content": user_msg},
        ]
    )

    return {
        "evaluation": {"status": result.status, "reason": result.reason},
        "final_summary": result.final_summary,
    }
