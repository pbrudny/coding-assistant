from typing import Literal

from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from app.config import settings
from app.prompts.templates import UNDERSTAND_SYSTEM
from app.state import AgentState


class TaskUnderstanding(BaseModel):
    goal: str
    likely_components: list[str]
    risk_level: Literal["low", "medium", "high"]
    requires_tests: bool


def understand(state: AgentState) -> dict:
    llm = ChatOpenAI(model=settings.model, api_key=settings.openai_api_key)
    structured = llm.with_structured_output(TaskUnderstanding)

    result: TaskUnderstanding = structured.invoke(
        [
            {"role": "system", "content": UNDERSTAND_SYSTEM},
            {"role": "user", "content": f"Task: {state['task']}"},
        ]
    )

    return {
        "goal": result.goal,
        "likely_components": result.likely_components,
        "risk_level": result.risk_level,
        "requires_tests": result.requires_tests,
    }
