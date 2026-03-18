from langgraph.graph import END, START, StateGraph

from .nodes import (
    catl_research_node,
    catl_strategy_node,
    compare_node,
    insight_node,
    lg_research_node,
    lg_strategy_node,
    market_node,
    report_node,
    swot_node,
)
from .router import route_after_catl_strategy, route_after_lg_strategy
from .state import WorkflowState


def build_graph():
    graph = StateGraph(WorkflowState)
    graph.add_node("market_node", market_node)
    graph.add_node("lg_research_node", lg_research_node)
    graph.add_node("catl_research_node", catl_research_node)
    graph.add_node("lg_strategy_node", lg_strategy_node)
    graph.add_node("catl_strategy_node", catl_strategy_node)
    graph.add_node("compare_node", compare_node)
    graph.add_node("swot_node", swot_node)
    graph.add_node("insight_node", insight_node)
    graph.add_node("report_node", report_node)

    graph.add_edge(START, "market_node")
    graph.add_edge("market_node", "lg_research_node")
    graph.add_edge("market_node", "catl_research_node")
    graph.add_edge("lg_research_node", "lg_strategy_node")
    graph.add_edge("catl_research_node", "catl_strategy_node")
    graph.add_conditional_edges(
        "lg_strategy_node",
        route_after_lg_strategy,
        {
            "lg_strategy_node": "lg_strategy_node",
            "lg_research_node": "lg_research_node",
            "catl_strategy_node": "catl_strategy_node",
            "compare_node": "compare_node",
        },
    )
    graph.add_conditional_edges(
        "catl_strategy_node",
        route_after_catl_strategy,
        {
            "catl_strategy_node": "catl_strategy_node",
            "catl_research_node": "catl_research_node",
            "lg_strategy_node": "lg_strategy_node",
            "compare_node": "compare_node",
        },
    )
    graph.add_edge("compare_node", "swot_node")
    graph.add_edge("swot_node", "insight_node")
    graph.add_edge("insight_node", "report_node")
    graph.add_edge("report_node", END)
    return graph.compile()
