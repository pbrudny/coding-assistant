from langgraph.graph import END, StateGraph

from app.config import settings
from app.nodes.evaluate import evaluate
from app.nodes.implement import implement
from app.nodes.planner import planner
from app.nodes.search import codebase_search
from app.nodes.test_runner import test_runner
from app.nodes.understand import understand
from app.state import AgentState


def _route_after_evaluate(state: AgentState) -> str:
    status = state.get("evaluation", {}).get("status", "failed")
    iteration = state.get("iteration_count", 0)
    if status == "success" or status == "failed" or iteration >= settings.max_iterations:
        return END
    return "implement"


def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    graph.add_node("understand", understand)
    graph.add_node("codebase_search", codebase_search)
    graph.add_node("planner", planner)
    graph.add_node("implement", implement)
    graph.add_node("test_runner", test_runner)
    graph.add_node("evaluate", evaluate)

    graph.set_entry_point("understand")
    graph.add_edge("understand", "codebase_search")
    graph.add_edge("codebase_search", "planner")
    graph.add_edge("planner", "implement")
    graph.add_edge("implement", "test_runner")
    graph.add_edge("test_runner", "evaluate")
    graph.add_conditional_edges("evaluate", _route_after_evaluate)

    return graph.compile()
