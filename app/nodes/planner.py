from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from app.config import settings
from app.prompts.templates import PLAN_SYSTEM
from app.state import AgentState


class ImplementationPlan(BaseModel):
    steps: list[str]
    files_to_modify: list[str]


def planner(state: AgentState) -> dict:
    llm = ChatOpenAI(model=settings.model, api_key=settings.openai_api_key)
    structured = llm.with_structured_output(ImplementationPlan)

    context = "\n\n".join(state.get("context_snippets", []))
    user_msg = (
        f"Goal: {state['goal']}\n\n"
        f"Known components: {', '.join(state.get('likely_components', []))}\n\n"
        f"Relevant code context:\n{context}"
    )

    result: ImplementationPlan = structured.invoke(
        [
            {"role": "system", "content": PLAN_SYSTEM},
            {"role": "user", "content": user_msg},
        ]
    )

    return {
        "implementation_plan": result.steps,
        "files_to_modify": result.files_to_modify,
    }
