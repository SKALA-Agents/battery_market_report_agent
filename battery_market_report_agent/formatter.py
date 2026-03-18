from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable, List

from .state import WorkflowState


def _escape_md(value: object) -> str:
    text = "" if value is None else str(value)
    return text.replace("|", "\\|").replace("\n", "<br>")


def _markdown_table(headers: List[str], rows: List[List[str]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(_escape_md(cell) for cell in row) + " |")
    return "\n".join(lines)


def _collect_reference_ids(state: WorkflowState) -> List[str]:
    ids = set()
    ids.update(state.get("market_context", {}).get("source_ids", []))
    for company in ("lg", "catl"):
        ids.update(state["companies"][company].get("analysis", {}).get("source_ids", []))
    ids.update(state.get("comparison_result", {}).get("source_ids", []))
    ids.update(state.get("swot_result", {}).get("lg", {}).get("source_ids", []))
    ids.update(state.get("swot_result", {}).get("catl", {}).get("source_ids", []))
    ids.update(state.get("insight_result", {}).get("source_ids", []))
    for strategy in state.get("insight_result", {}).get("selected_strategies", []):
        ids.update(strategy.get("source_ids", []))
    return sorted(ids)


def _reference_index(state: WorkflowState) -> Dict[str, int]:
    return {source_id: idx for idx, source_id in enumerate(_collect_reference_ids(state), start=1)}


def _ref_links(state: WorkflowState, source_ids: Iterable[str]) -> str:
    index = _reference_index(state)
    links = []
    for source_id in source_ids:
        number = index.get(source_id)
        if number is None:
            continue
        links.append(f"[{number}](#ref-{number})")
    return " ".join(dict.fromkeys(links))


def _append_refs(text: str, refs: str) -> str:
    text = text.strip()
    if not refs:
        return text
    return f"{text} {refs}".strip()


def _bullet_lines(items: List[str], refs: str = "") -> List[str]:
    if not items:
        return ["- 정보 부족"]
    lines = []
    for item in items:
        lines.append(f"- {_append_refs(item, refs)}")
    return lines


def _metrics_table(state: WorkflowState) -> str:
    rows: List[List[str]] = []
    lg_metrics = state["companies"]["lg"].get("analysis", {}).get("key_metrics", [])
    catl_metrics = state["companies"]["catl"].get("analysis", {}).get("key_metrics", [])
    metric_map = {}
    for metric in lg_metrics:
        metric_map.setdefault(metric["label"], {})["lg"] = metric
    for metric in catl_metrics:
        metric_map.setdefault(metric["label"], {})["catl"] = metric
    for label, data in metric_map.items():
        lg_value = data.get("lg", {}).get("value")
        catl_value = data.get("catl", {}).get("value")
        unit = data.get("lg", {}).get("unit") or data.get("catl", {}).get("unit", "")
        period = data.get("lg", {}).get("period") or data.get("catl", {}).get("period", "")
        rows.append(
            [
                label,
                "" if lg_value is None else f"{lg_value}",
                "" if catl_value is None else f"{catl_value}",
                unit,
                period,
                _ref_links(state, data.get("lg", {}).get("source_ids", []) + data.get("catl", {}).get("source_ids", [])),
            ]
        )
    if not rows:
        return "_공통 비교 가능한 정량 지표가 부족함_"
    return _markdown_table(["지표", "LGES", "CATL", "단위", "시점", "참조"], rows)


def _winner_rationale(row: dict) -> str:
    advantage = row.get("advantage", "")
    if advantage == "LGES":
        return f"LGES 우위: {row.get('lg_summary', '정보 부족')}"
    if advantage == "CATL":
        return f"CATL 우위: {row.get('catl_summary', '정보 부족')}"
    if advantage == "parity":
        return "뚜렷한 우위 제한적: 양사 모두 유사한 수준의 근거가 확인됨"
    return "근거 부족으로 우위 판단 보류"


def _comparison_table(state: WorkflowState) -> str:
    rows = []
    for row in state.get("comparison_result", {}).get("comparison_table", []):
        rows.append(
            [
                row.get("criterion", ""),
                row.get("lg_summary", "").replace("\n", " "),
                row.get("catl_summary", "").replace("\n", " "),
                row.get("advantage", ""),
                _append_refs(_winner_rationale(row), _ref_links(state, row.get("evidence", []))),
            ]
        )
    return _markdown_table(["평가 기준", "LGES", "CATL", "우위", "우위 판단 근거"], rows)


def _swot_table(state: WorkflowState, company: str, label: str) -> str:
    swot = state.get("swot_result", {}).get(company, {})
    refs = _ref_links(state, swot.get("source_ids", []))
    rows = [
        ["Strengths", "<br>".join(_bullet_lines(swot.get("strengths", []))), refs],
        ["Weaknesses", "<br>".join(_bullet_lines(swot.get("weaknesses", []))), refs],
        ["Opportunities", "<br>".join(_bullet_lines(swot.get("opportunities", []))), refs],
        ["Threats", "<br>".join(_bullet_lines(swot.get("threats", []))), refs],
    ]
    return f"### {label}\n\n" + _markdown_table(["구분", "내용", "참조"], rows)


def _grouped_insights(state: WorkflowState) -> str:
    strategies = state.get("insight_result", {}).get("selected_strategies", [])
    if not strategies:
        return "_전략 인사이트가 생성되지 않았음_"

    groups: Dict[str, List[dict]] = {"SO": [], "ST": [], "WO": [], "WT": []}
    for strategy in strategies:
        strategy_type = strategy.get("type", "").upper()
        if strategy_type in groups:
            groups[strategy_type].append(strategy)

    title_map = {
        "SO": "SO 전략",
        "ST": "ST 전략",
        "WO": "WO 전략",
        "WT": "WT 전략",
    }
    sections: List[str] = []
    fallback_refs = _ref_links(state, state.get("swot_result", {}).get("lg", {}).get("source_ids", []))
    for key in ("SO", "ST", "WO", "WT"):
        items = groups[key]
        if not items:
            continue
        rows = []
        for item in items:
            refs = _ref_links(state, item.get("source_ids", [])) or fallback_refs
            rows.append(
                [
                    item.get("title", ""),
                    item.get("rationale", ""),
                    item.get("priority", ""),
                    refs,
                ]
            )
        sections.append(f"### {title_map[key]}\n\n" + _markdown_table(["전략 제안", "실행 인사이트", "우선순위", "참조"], rows))
    return "\n\n".join(sections)


def _reference_section(state: WorkflowState) -> List[str]:
    source_registry = state.get("source_registry", {})
    lines: List[str] = []
    for idx, source_id in enumerate(_collect_reference_ids(state), start=1):
        source = source_registry.get(source_id)
        if not source:
            continue
        publisher = source.get("publisher") or "Unknown"
        date = source.get("date") or "n.d."
        title = source.get("title") or source_id
        url = source.get("url") or ""
        lines.append(f'<a id="ref-{idx}"></a>{idx}. {publisher} ({date}). [{title}]({url})')
        lines.append("")
    return lines


def render_markdown_report(state: WorkflowState, chart_paths: Dict[str, str]) -> str:
    report = state.get("final_report", {})
    summary = report.get("summary", {})
    market_refs = _ref_links(state, state.get("market_context", {}).get("source_ids", []))
    lg_refs = _ref_links(state, state["companies"]["lg"].get("analysis", {}).get("source_ids", []))
    catl_refs = _ref_links(state, state["companies"]["catl"].get("analysis", {}).get("source_ids", []))
    comparison_refs = _ref_links(state, state.get("comparison_result", {}).get("source_ids", []))
    conclusion_refs = _ref_links(
        state,
        state.get("comparison_result", {}).get("source_ids", [])
        + state.get("insight_result", {}).get("source_ids", [])
        + state.get("swot_result", {}).get("lg", {}).get("source_ids", []),
    )
    lines = [
        "# 배터리 시장 전략 비교 보고서",
        "",
        "## 1. Executive Summary",
        "",
        "### 핵심 결론",
    ]
    for item in summary.get("key_conclusions", []):
        lines.append(f"- {item}")
    lines.extend(["", "### 주요 인사이트"])
    for item in summary.get("key_insights", []):
        lines.append(f"- {item}")
    lines.extend(["", "### 의사결정 포인트"])
    for item in summary.get("decision_points", []):
        lines.append(f"- {item}")

    lines.extend(
        [
            "",
            "## 2. 산업 및 시장 배경",
            "",
            _append_refs(report.get("market_background", ""), market_refs),
            "",
            "## 3. 기업별 전략 분석",
            "",
            "### 3.1 LG에너지솔루션 전략 분석",
            "",
            _append_refs(report.get("lg_strategy", ""), lg_refs),
            "",
            "### 3.2 CATL 전략 분석",
            "",
            _append_refs(report.get("catl_strategy", ""), catl_refs),
            "",
            "### 3.3 핵심 정량 지표",
            "",
            _metrics_table(state),
            "",
            "## 4. 기업 비교 분석",
            "",
            _append_refs(report.get("comparison_analysis", ""), comparison_refs),
            "",
            "### 4.1 평가 기준별 비교표",
            "",
            _comparison_table(state),
            "",
            "## 5. SWOT 분석",
            "",
            _swot_table(state, "lg", "5.1 LG에너지솔루션 SWOT"),
            "",
            _swot_table(state, "catl", "5.2 CATL SWOT"),
            "",
            "## 6. LG 에너지 솔루션의 전략적 인사이트 (SO/ST/WO/WT)",
            "",
            _grouped_insights(state),
            "",
            "## 7. 종합 시사점",
            "",
            _append_refs(report.get("conclusion_or_implications", ""), conclusion_refs),
            "",
            "## 8. References",
            "",
        ]
    )
    lines.extend(_reference_section(state))
    return "\n".join(lines).strip() + "\n"


def write_markdown_report(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_state_snapshot(path: Path, state: WorkflowState) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
