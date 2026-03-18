from __future__ import annotations

import json
from typing import Any, Dict, List

from .schemas import (
    CompanyAnalysisModel,
    FinalReportModel,
    InsightResultModel,
    MarketContextModel,
    SwotResultModel,
)
from .state import (
    ANALYSIS_CRITERIA,
    ComparisonResult,
    RetrievalDiagnostics,
    RetrievalStatus,
    ValidationRecord,
    WorkflowState,
)
from .tools import (
    COMPANY_LABELS,
    TavilySearchTool,
    evaluate_retrieval,
    filter_company_sources,
    make_web_search_record,
    mark_web_search,
    merge_sources,
    normalize_search_results,
    retrieve_evidence_snippets,
    source_registry_update,
    structured_llm,
)
from .vector_db import retrieve_static


def _market_queries(user_query: str) -> List[str]:
    return [
        "global battery market EV slowdown ESS expansion 2025 2026",
        "battery industry policy IRA Europe China 2025 2026",
        "battery supply chain and chemistry trends 2025 2026",
        user_query,
    ]


def _company_queries(company: str, user_query: str) -> List[str]:
    label = COMPANY_LABELS[company]
    return [
        f"{label} portfolio diversification EV ESS strategy 2025 2026",
        f"{label} supply chain global expansion technology roadmap",
        f"{label} partnerships OEM ESS annual report strategy",
        f"{user_query} {label}",
    ]


def _risk_queries(company: str) -> List[str]:
    label = COMPANY_LABELS[company]
    return [
        f"{label} risk challenge pressure criticism battery 2025 2026",
        f"{label} profitability slowdown utilization restructuring 2025 2026",
    ]


def _market_risk_queries() -> List[str]:
    return [
        "battery industry risk oversupply margin pressure regulation burden 2025 2026",
        "battery safety recycling compliance pressure 2025 2026",
    ]


def _format_sources_for_prompt(sources: List[dict]) -> str:
    return "\n".join(
        json.dumps(
            {
                "source_id": source["source_id"],
                "title": source["title"],
                "publisher": source["publisher"],
                "date": source["date"],
                "criterion_tags": source.get("criterion_tags", []),
                "excerpt": source["excerpt"],
                "numeric_facts": source["numeric_facts"],
            },
            ensure_ascii=False,
        )
        for source in sources
    )


def _validation(decision: str, reason: str, missing_items: List[str], target_node: str | None = None) -> ValidationRecord:
    record: ValidationRecord = {
        "decision": decision,
        "reason": reason,
        "missing_items": missing_items,
    }
    if target_node:
        record["target_node"] = target_node
    return record


def _maybe_web_search(scope: str, base_sources: List[dict], status: RetrievalStatus, diagnostics: RetrievalDiagnostics, queries: List[str]) -> tuple[List[dict], RetrievalStatus, List[dict]]:
    search_tool = TavilySearchTool()
    if status["sufficient"] or not queries:
        return base_sources, status, []
    new_results = []
    history = []
    for query in queries:
        raw_results = search_tool.search(query, max_results=3)
        normalized = normalize_search_results(raw_results, scope)
        if scope in {"lg", "catl"}:
            normalized = filter_company_sources(scope, normalized)
        if normalized:
            new_results = merge_sources(new_results, normalized)
            history.append(make_web_search_record(query, status["reason"], [item["source_id"] for item in normalized]))
    merged = merge_sources(base_sources, new_results)
    if new_results:
        status = mark_web_search(status, status["reason"])
    return merged, status, history


def _select_market_queries(user_query: str, status: RetrievalStatus) -> List[str]:
    queries = []
    if "자료 부족" in status["reason"]:
        queries.extend(_market_queries(user_query))
    if "자료 노후" in status["reason"] or "출처 다양성 부족" in status["reason"] or "반증 부족" in status["reason"]:
        queries.extend(_market_risk_queries())
    return list(dict.fromkeys(queries))


def _select_company_queries(company: str, user_query: str, status: RetrievalStatus) -> List[str]:
    queries = []
    if "자료 부족" in status["reason"]:
        queries.extend(_company_queries(company, user_query))
    if "자료 노후" in status["reason"] or "반증 부족" in status["reason"] or "출처 다양성 부족" in status["reason"]:
        queries.extend(_risk_queries(company))
    return list(dict.fromkeys(queries))


def market_node(state: WorkflowState) -> Dict[str, Any]:
    static_docs = retrieve_static("market", _market_queries(state["user_query"]))
    static_sources = [doc.metadata for doc in static_docs]
    status, diagnostics = evaluate_retrieval(static_sources, "market")
    merged_sources, status, history = _maybe_web_search(
        "market",
        static_sources,
        status,
        diagnostics,
        _select_market_queries(state["user_query"], status),
    )
    status, diagnostics = evaluate_retrieval(merged_sources, "market")
    if history:
        status["used_web_search"] = True

    snippets = retrieve_evidence_snippets(
        merged_sources,
        [
            "global battery market demand and capacity trend",
            "policy and regulation affecting battery strategy",
            "supply chain and chemistry risk",
        ],
    )
    result = structured_llm(MarketContextModel).invoke(
        (
            "다음 근거만 사용하여 한국어로 시장 환경을 구조화하라.\n"
            "LG에너지솔루션과 CATL 비교에 필요한 공통 프레임을 만들어야 한다.\n"
            "과장하지 말고, 근거가 약하면 정보 부족이라고 명시하라.\n\n"
            f"근거:\n{chr(10).join(snippets)}"
        )
    )
    market_context = result.model_dump()
    market_context["evaluation_guidance_for_7_criteria"] = ANALYSIS_CRITERIA
    return {
        "market_context": market_context,
        "market_retrieval_status": status,
        "market_retrieval_diagnostics": diagnostics,
        "market_web_search_history": history,
        "source_registry": source_registry_update(merged_sources),
        "step_status": {"market_node": "pass"},
        "validation_result": {"market_node": _validation("pass", "시장 컨텍스트 생성 완료", [])},
    }


def _research_company(state: WorkflowState, company: str) -> Dict[str, Any]:
    branch = dict(state["companies"][company])
    static_docs = retrieve_static(company, _company_queries(company, state["user_query"]))
    static_sources = [doc.metadata for doc in static_docs]
    status, diagnostics = evaluate_retrieval(static_sources, company)
    merged_sources, status, history = _maybe_web_search(
        company,
        static_sources,
        status,
        diagnostics,
        _select_company_queries(company, state["user_query"], status),
    )
    status, diagnostics = evaluate_retrieval(merged_sources, company)
    if history:
        status["used_web_search"] = True
    branch["raw_docs"] = merged_sources
    branch["retrieval_status"] = status
    branch["retrieval_diagnostics"] = diagnostics
    branch["web_search_history"] = history
    branch["kb_update_count"] = len(history)
    branch["step_status"] = {**branch.get("step_status", {}), "research_node": "pass"}
    branch["validation_result"] = {
        **branch.get("validation_result", {}),
        "research_node": _validation("pass", "기업 자료 확보 완료", diagnostics.get("missing_criteria", [])),
    }
    branch["ready"] = False
    return {
        "companies": {company: branch},
        "source_registry": source_registry_update(merged_sources),
    }


def lg_research_node(state: WorkflowState) -> Dict[str, Any]:
    return _research_company(state, "lg")


def catl_research_node(state: WorkflowState) -> Dict[str, Any]:
    return _research_company(state, "catl")


def _find_section(analysis: dict, criterion: str) -> dict:
    for item in analysis.get("criteria_sections", []):
        if item.get("criterion") == criterion:
            return item
    return {}


def _validate_analysis(analysis: dict, company: str) -> ValidationRecord:
    missing = [criterion for criterion in ANALYSIS_CRITERIA if not _find_section(analysis, criterion)]
    if missing:
        return _validation("retry", f"{company} 전략 분석 기준 누락", missing)
    weak = [item["criterion"] for item in analysis.get("criteria_sections", []) if not item.get("source_ids")]
    if weak:
        return _validation("loop", f"{company} 전략 분석 근거 부족", weak, f"{company}_research_node")
    return _validation("pass", f"{company} 전략 분석 완료", [])


def _strategy_for_company(state: WorkflowState, company: str) -> Dict[str, Any]:
    branch = dict(state["companies"][company])
    sources = branch.get("raw_docs", [])
    snippets = retrieve_evidence_snippets(
        sources,
        [
            f"{COMPANY_LABELS[company]} portfolio and ESS strategy",
            f"{COMPANY_LABELS[company]} technology and chemistry roadmap",
            f"{COMPANY_LABELS[company]} supply chain and global expansion",
            f"{COMPANY_LABELS[company]} customer partnership and risk response",
        ],
    )
    result = structured_llm(CompanyAnalysisModel).invoke(
        (
            f"당신은 {COMPANY_LABELS[company]}만 분석한다.\n"
            "다음 시장 맥락과 기업 근거만 사용하여 한국어로 7개 평가 기준 분석을 작성하라.\n"
            "각 기준마다 summary, strengths, weaknesses, source_ids를 포함하라.\n"
            "핵심 수치가 있으면 key_metrics에 넣고, 불확실한 부분은 uncertainty_notes에 기록하라.\n"
            "타 기업 정보는 사용하지 말라.\n\n"
            f"시장 맥락:\n{json.dumps(state.get('market_context', {}), ensure_ascii=False)}\n\n"
            f"근거 문서:\n{_format_sources_for_prompt(sources)}\n\n"
            f"검색된 근거 snippet:\n{chr(10).join(snippets)}"
        )
    )
    analysis = result.model_dump()
    valid_ids = {source["source_id"] for source in sources}
    analysis["source_ids"] = [sid for sid in analysis.get("source_ids", []) if sid in valid_ids]
    for item in analysis.get("criteria_sections", []):
        item["source_ids"] = [sid for sid in item.get("source_ids", []) if sid in valid_ids]
    validation = _validate_analysis(analysis, company)
    branch["analysis"] = analysis
    branch["validation_result"] = {**branch.get("validation_result", {}), "strategy_node": validation}
    branch["step_status"] = {**branch.get("step_status", {}), "strategy_node": "pass" if validation["decision"] == "pass" else "fail"}
    branch["ready"] = validation["decision"] == "pass"
    return {"companies": {company: branch}}


def lg_strategy_node(state: WorkflowState) -> Dict[str, Any]:
    return _strategy_for_company(state, "lg")


def catl_strategy_node(state: WorkflowState) -> Dict[str, Any]:
    return _strategy_for_company(state, "catl")


def _derive_difference(lg_item: dict, catl_item: dict) -> str:
    if not lg_item and not catl_item:
        return "정보 부족"
    lg_summary = lg_item.get("summary", "정보 부족")
    catl_summary = catl_item.get("summary", "정보 부족")
    if lg_summary == catl_summary:
        return "유의미한 차이 제한적"
    return f"LGES는 {lg_summary}, CATL은 {catl_summary}"


def _determine_advantage(lg_item: dict, catl_item: dict) -> str:
    lg_score = len(lg_item.get("strengths", [])) - len(lg_item.get("weaknesses", []))
    catl_score = len(catl_item.get("strengths", [])) - len(catl_item.get("weaknesses", []))
    if not lg_item.get("source_ids") or not catl_item.get("source_ids"):
        return "undetermined"
    if lg_score > catl_score:
        return "LGES"
    if catl_score > lg_score:
        return "CATL"
    return "parity"


def comparison_engine(lg_analysis: dict, catl_analysis: dict) -> ComparisonResult:
    rows = []
    for criterion in ANALYSIS_CRITERIA:
        lg_item = _find_section(lg_analysis, criterion)
        catl_item = _find_section(catl_analysis, criterion)
        rows.append(
            {
                "criterion": criterion,
                "lg_summary": lg_item.get("summary", "정보 부족"),
                "catl_summary": catl_item.get("summary", "정보 부족"),
                "lg_evidence_count": len(lg_item.get("source_ids", [])),
                "catl_evidence_count": len(catl_item.get("source_ids", [])),
                "difference": _derive_difference(lg_item, catl_item),
                "advantage": _determine_advantage(lg_item, catl_item),
                "evidence": sorted(set(lg_item.get("source_ids", []) + catl_item.get("source_ids", []))),
            }
        )
    return {
        "comparison_table": rows,
        "key_differences": [row["difference"] for row in rows if row["difference"] != "유의미한 차이 제한적"],
        "competitive_advantages": [f"{row['criterion']}: {row['advantage']}" for row in rows if row["advantage"] not in {"undetermined", "parity"}],
        "source_ids": sorted({sid for row in rows for sid in row["evidence"]}),
    }


def compare_node(state: WorkflowState) -> Dict[str, Any]:
    result = comparison_engine(
        state["companies"]["lg"].get("analysis", {}),
        state["companies"]["catl"].get("analysis", {}),
    )
    return {
        "comparison_result": result,
        "validation_result": {"compare_node": _validation("pass", "비교 분석 완료", [])},
        "step_status": {"compare_node": "pass"},
    }


def swot_node(state: WorkflowState) -> Dict[str, Any]:
    result = structured_llm(SwotResultModel).invoke(
        (
            "다음 비교 결과와 기업별 분석 결과만 사용하여 한국어로 기업별 SWOT을 생성하라.\n"
            "각 기업에 대해 strengths, weaknesses, opportunities, threats, source_ids를 반환하라.\n\n"
            f"시장 맥락:\n{json.dumps(state.get('market_context', {}), ensure_ascii=False)}\n\n"
            f"비교 결과:\n{json.dumps(state.get('comparison_result', {}), ensure_ascii=False)}\n\n"
            f"LG 분석:\n{json.dumps(state['companies']['lg'].get('analysis', {}), ensure_ascii=False)}\n\n"
            f"CATL 분석:\n{json.dumps(state['companies']['catl'].get('analysis', {}), ensure_ascii=False)}"
        )
    )
    return {
        "swot_result": result.model_dump(),
        "validation_result": {"swot_node": _validation("pass", "SWOT 생성 완료", [])},
        "step_status": {"swot_node": "pass"},
    }


def insight_node(state: WorkflowState) -> Dict[str, Any]:
    result = structured_llm(InsightResultModel).invoke(
        (
            "다음 SWOT만 사용하여 LG에너지솔루션 관점의 SO/ST/WO/WT 전략 인사이트를 한국어로 생성하라.\n"
            "새로운 사실을 만들지 말고, selected_strategies와 strategic_implications를 반환하라.\n\n"
            f"SWOT:\n{json.dumps(state.get('swot_result', {}), ensure_ascii=False)}"
        )
    )
    return {
        "insight_result": result.model_dump(),
        "validation_result": {"insight_node": _validation("pass", "인사이트 생성 완료", [])},
        "step_status": {"insight_node": "pass"},
    }


def _collect_reference_ids(state: WorkflowState) -> List[str]:
    ids = set()
    for company in ("lg", "catl"):
        ids.update(state["companies"][company].get("analysis", {}).get("source_ids", []))
    ids.update(state.get("comparison_result", {}).get("source_ids", []))
    ids.update(state.get("swot_result", {}).get("lg", {}).get("source_ids", []))
    ids.update(state.get("swot_result", {}).get("catl", {}).get("source_ids", []))
    ids.update(state.get("insight_result", {}).get("source_ids", []))
    ids.update(state.get("market_context", {}).get("source_ids", []))
    return sorted(ids)


def report_node(state: WorkflowState) -> Dict[str, Any]:
    result = structured_llm(FinalReportModel).invoke(
        (
            "다음 입력만 사용하여 한국어 의사결정 지원 보고서를 작성하라.\n"
            "summary는 key_conclusions, key_insights, decision_points를 포함해야 한다.\n"
            "시장 배경, LG 전략, CATL 전략, 비교 분석, SWOT 분석, LG 전략 인사이트, 종합 시사점을 각각 서술하라.\n"
            "과장하지 말고, 근거가 부족하면 정보 부족이라고 명시하라.\n\n"
            f"시장 맥락:\n{json.dumps(state.get('market_context', {}), ensure_ascii=False)}\n\n"
            f"LG 분석:\n{json.dumps(state['companies']['lg'].get('analysis', {}), ensure_ascii=False)}\n\n"
            f"CATL 분석:\n{json.dumps(state['companies']['catl'].get('analysis', {}), ensure_ascii=False)}\n\n"
            f"비교:\n{json.dumps(state.get('comparison_result', {}), ensure_ascii=False)}\n\n"
            f"SWOT:\n{json.dumps(state.get('swot_result', {}), ensure_ascii=False)}\n\n"
            f"인사이트:\n{json.dumps(state.get('insight_result', {}), ensure_ascii=False)}"
        )
    )
    source_registry = state.get("source_registry", {})
    references = []
    for source_id in _collect_reference_ids(state):
        source = source_registry.get(source_id)
        if not source:
            continue
        references.append(
            f"{source['publisher']} ({source['date'] or 'n.d.'}). {source['title']}. {source['url']}"
        )
    return {
        "final_report": result.model_dump(),
        "references": references,
        "validation_result": {"report_node": _validation("pass", "최종 보고서 생성 완료", [])},
        "step_status": {"report_node": "pass"},
    }
