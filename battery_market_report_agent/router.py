from __future__ import annotations

from .state import WorkflowState


def _branch_decision(state: WorkflowState, company: str) -> str:
    return state["companies"][company].get("validation_result", {}).get("strategy_node", {}).get("decision", "pass")


def can_run_compare(state: WorkflowState) -> bool:
    return (
        state["companies"]["lg"]["ready"]
        and state["companies"]["catl"]["ready"]
        and _branch_decision(state, "lg") == "pass"
        and _branch_decision(state, "catl") == "pass"
    )


def route_after_lg_strategy(state: WorkflowState) -> str:
    decision = _branch_decision(state, "lg")
    if decision == "retry":
        return "lg_strategy_node"
    if decision == "loop":
        return state["companies"]["lg"]["validation_result"]["strategy_node"].get("target_node", "lg_research_node")
    return "compare_node" if can_run_compare(state) else "catl_strategy_node"


def route_after_catl_strategy(state: WorkflowState) -> str:
    decision = _branch_decision(state, "catl")
    if decision == "retry":
        return "catl_strategy_node"
    if decision == "loop":
        return state["companies"]["catl"]["validation_result"]["strategy_node"].get("target_node", "catl_research_node")
    return "compare_node" if can_run_compare(state) else "lg_strategy_node"
