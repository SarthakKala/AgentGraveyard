from typing import Any

from langgraph.graph import END, StateGraph
from sqlalchemy.orm import Session

from core.coroner_agent import (
    CornerState,
    classify_failure_node,
    diagnose_failure_node,
    query_graveyard_node,
    store_failure_node,
    synthesize_solution_node,
)


def build_agent_graph(db: Session) -> Any:
    graph = StateGraph(CornerState)
    graph.add_node("classify", classify_failure_node)
    graph.add_node("diagnose", diagnose_failure_node)
    graph.add_node("query_graveyard", query_graveyard_node)
    graph.add_node("synthesize", synthesize_solution_node)
    graph.add_node("store", lambda state: store_failure_node(state, db))

    graph.set_entry_point("classify")
    graph.add_edge("classify", "diagnose")
    graph.add_edge("diagnose", "query_graveyard")
    graph.add_edge("query_graveyard", "synthesize")
    graph.add_edge("synthesize", "store")
    graph.add_edge("store", END)

    return graph.compile()
