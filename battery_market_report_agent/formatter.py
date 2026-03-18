from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from .state import WorkflowState


def _markdown_table(headers: List[str], rows: List[List[str]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


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
            ]
        )
    if not rows:
        return "_공통 비교 가능한 정량 지표가 부족함_"
    return _markdown_table(["지표", "LGES", "CATL", "단위", "시점"], rows)


def _comparison_table(state: WorkflowState) -> str:
    rows = []
    for row in state.get("comparison_result", {}).get("comparison_table", []):
        rows.append(
            [
                row.get("criterion", ""),
                row.get("lg_summary", "").replace("\n", " "),
                row.get("catl_summary", "").replace("\n", " "),
                row.get("advantage", ""),
            ]
        )
    return _markdown_table(["평가 기준", "LGES", "CATL", "우위"], rows)


def _chart_md(chart_paths: Dict[str, str]) -> str:
    parts = []
    titles = {
        "criterion_coverage": "평가 기준별 근거 수",
        "swot_counts": "SWOT 항목 수 비교",
        "key_metrics": "공통 핵심 수치 비교",
    }
    for key, path in chart_paths.items():
        parts.append(f"### {titles.get(key, key)}\n\n![]({path})")
    return "\n\n".join(parts)


def render_markdown_report(state: WorkflowState, chart_paths: Dict[str, str]) -> str:
    report = state.get("final_report", {})
    summary = report.get("summary", {})
    references = state.get("references", [])
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
            report.get("market_background", ""),
            "",
            "## 3. 기업별 전략 분석",
            "",
            "### 3.1 LG에너지솔루션 전략 분석",
            "",
            report.get("lg_strategy", ""),
            "",
            "### 3.2 CATL 전략 분석",
            "",
            report.get("catl_strategy", ""),
            "",
            "### 3.3 핵심 정량 지표",
            "",
            _metrics_table(state),
            "",
            "## 4. 기업 비교 분석",
            "",
            report.get("comparison_analysis", ""),
            "",
            "### 4.1 평가 기준별 비교표",
            "",
            _comparison_table(state),
            "",
            "## 5. SWOT 분석",
            "",
            report.get("swot_analysis", ""),
            "",
            "## 6. LG 에너지 솔루션의 전략적 인사이트 (SO/ST/WO/WT)",
            "",
            report.get("lg_insights", ""),
            "",
            "## 7. 데이터 기반 그래프",
            "",
            _chart_md(chart_paths),
            "",
            "## 8. 종합 시사점",
            "",
            report.get("conclusion_or_implications", ""),
            "",
            "## 9. References",
            "",
        ]
    )
    for idx, reference in enumerate(references, start=1):
        lines.append(f"{idx}. {reference}")
    return "\n".join(lines).strip() + "\n"


def write_markdown_report(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_state_snapshot(path: Path, state: WorkflowState) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
