from __future__ import annotations

from typing import Annotated, Any, Dict, List, Literal, Optional, TypedDict

from typing_extensions import NotRequired


ANALYSIS_CRITERIA = [
    "포트폴리오 다양성",
    "기술 경쟁력",
    "시장 대응력",
    "공급망 전략",
    "고객/파트너 구조",
    "글로벌 확장성",
    "리스크 대응력",
]

NodeStatus = Literal["pending", "running", "pass", "fail"]
ValidationDecision = Literal["pass", "retry", "loop", "fail"]


def merge_dicts(left: dict, right: dict | None) -> dict:
    merged = dict(left or {})
    if right:
        merged.update(right)
    return merged


class SourceMeta(TypedDict):
    source_id: str
    source_type: str
    title: str
    url: str
    date: str
    publisher: str
    excerpt: str
    numeric_facts: List[str]
    reliability_note: str
    company_scope: str
    criterion_tags: List[str]
    sentiment_side: str
    region_tags: List[str]


class KeyMetric(TypedDict):
    label: str
    value: Optional[float]
    unit: str
    period: str
    source_ids: List[str]


class CriteriaSection(TypedDict):
    criterion: str
    summary: str
    evidence: List[str]
    strengths: List[str]
    weaknesses: List[str]
    source_ids: List[str]


class CompanyAnalysis(TypedDict):
    company: str
    executive_takeaway: str
    criteria_sections: List[CriteriaSection]
    strengths: List[str]
    weaknesses: List[str]
    key_metrics: List[KeyMetric]
    source_ids: List[str]
    uncertainty_notes: List[str]


class ComparisonRow(TypedDict):
    criterion: str
    lg_summary: str
    catl_summary: str
    lg_evidence_count: int
    catl_evidence_count: int
    difference: str
    advantage: str
    evidence: List[str]


class ComparisonResult(TypedDict):
    comparison_table: List[ComparisonRow]
    key_differences: List[str]
    competitive_advantages: List[str]
    source_ids: List[str]


class CompanySwot(TypedDict):
    strengths: List[str]
    weaknesses: List[str]
    opportunities: List[str]
    threats: List[str]
    source_ids: List[str]


class SwotResult(TypedDict):
    lg: CompanySwot
    catl: CompanySwot


class SelectedStrategy(TypedDict):
    type: str
    title: str
    rationale: str
    related_swot: List[str]
    priority: str
    source_ids: List[str]


class InsightResult(TypedDict):
    selected_strategies: List[SelectedStrategy]
    strategic_implications: List[str]
    source_ids: List[str]


class ValidationRecord(TypedDict):
    decision: ValidationDecision
    reason: str
    missing_items: List[str]
    target_node: NotRequired[str]


class RetrievalStatus(TypedDict):
    sufficient: bool
    used_web_search: bool
    reason: List[str]
    last_updated_at: str


class RetrievalDiagnostics(TypedDict):
    coverage_ok: bool
    freshness_ok: bool
    diversity_ok: bool
    counter_evidence_ok: bool
    missing_criteria: List[str]
    stale_sources: List[str]
    source_type_distribution: Dict[str, int]
    notes: List[str]


class WebSearchRecord(TypedDict):
    query: str
    trigger_reason: List[str]
    added_source_ids: List[str]
    executed_at: str


class SummaryBlock(TypedDict):
    key_conclusions: List[str]
    key_insights: List[str]
    decision_points: List[str]


class FinalReport(TypedDict):
    summary: SummaryBlock
    market_background: str
    lg_strategy: str
    catl_strategy: str
    comparison_analysis: str
    swot_analysis: str
    lg_insights: str
    conclusion_or_implications: str


class BranchState(TypedDict):
    raw_docs: NotRequired[List[SourceMeta]]
    analysis: NotRequired[CompanyAnalysis]
    step_status: Dict[str, NodeStatus]
    retry_counts: Dict[str, int]
    loop_counts: Dict[str, int]
    validation_result: Dict[str, ValidationRecord]
    ready: bool
    retrieval_status: NotRequired[RetrievalStatus]
    retrieval_diagnostics: NotRequired[RetrievalDiagnostics]
    web_search_history: NotRequired[List[WebSearchRecord]]
    kb_update_count: int


class WorkflowState(TypedDict):
    user_query: str
    market_context: NotRequired[Dict[str, Any]]
    market_retrieval_status: NotRequired[RetrievalStatus]
    market_retrieval_diagnostics: NotRequired[RetrievalDiagnostics]
    market_web_search_history: NotRequired[List[WebSearchRecord]]
    companies: Annotated[Dict[str, BranchState], merge_dicts]
    comparison_result: NotRequired[ComparisonResult]
    swot_result: NotRequired[SwotResult]
    insight_result: NotRequired[InsightResult]
    final_report: NotRequired[FinalReport]
    source_registry: NotRequired[Annotated[Dict[str, SourceMeta], merge_dicts]]
    references: NotRequired[List[str]]
    chart_paths: NotRequired[Dict[str, str]]
    step_status: Dict[str, NodeStatus]
    retry_counts: Dict[str, int]
    loop_counts: Dict[str, int]
    current_step: NotRequired[str]
    error_message: NotRequired[str]
    validation_result: Dict[str, ValidationRecord]


def make_initial_branch_state() -> BranchState:
    return BranchState(
        step_status={},
        retry_counts={},
        loop_counts={},
        validation_result={},
        ready=False,
        kb_update_count=0,
    )


def make_initial_state(query: str) -> WorkflowState:
    return WorkflowState(
        user_query=query,
        companies={
            "lg": make_initial_branch_state(),
            "catl": make_initial_branch_state(),
        },
        step_status={},
        retry_counts={},
        loop_counts={},
        validation_result={},
        source_registry={},
    )
