from langgraph.graph import StateGraph

from app.state import AgentState

MAX_ITERATIONS = 3


def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)
    # Nodes and edges will be wired here as each node module is implemented.
    return graph
