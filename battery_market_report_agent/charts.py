from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import matplotlib.pyplot as plt
import numpy as np

from .state import ANALYSIS_CRITERIA, WorkflowState


plt.rcParams["font.family"] = ["DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


def _save_chart(fig, path: Path) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return str(path)


def criterion_coverage_chart(state: WorkflowState, output_dir: Path) -> str:
    lg_analysis = state["companies"]["lg"].get("analysis", {})
    catl_analysis = state["companies"]["catl"].get("analysis", {})
    lg_counts: List[int] = []
    catl_counts: List[int] = []
    for criterion in ANALYSIS_CRITERIA:
        lg_count = 0
        catl_count = 0
        for item in lg_analysis.get("criteria_sections", []):
            if item.get("criterion") == criterion:
                lg_count = len(item.get("source_ids", []))
        for item in catl_analysis.get("criteria_sections", []):
            if item.get("criterion") == criterion:
                catl_count = len(item.get("source_ids", []))
        lg_counts.append(lg_count)
        catl_counts.append(catl_count)

    x = np.arange(len(ANALYSIS_CRITERIA))
    width = 0.35
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.bar(x - width / 2, lg_counts, width, label="LGES", color="#1f77b4")
    ax.bar(x + width / 2, catl_counts, width, label="CATL", color="#ff7f0e")
    ax.set_title("Evidence Count by Criterion")
    ax.set_ylabel("Evidence Count")
    ax.set_xticks(x)
    ax.set_xticklabels(ANALYSIS_CRITERIA, rotation=25, ha="right")
    ax.legend()
    return _save_chart(fig, output_dir / "criterion_coverage.png")


def swot_count_chart(state: WorkflowState, output_dir: Path) -> str | None:
    swot = state.get("swot_result")
    if not swot:
        return None
    labels = ["Strengths", "Weaknesses", "Opportunities", "Threats"]
    lg_counts = [
        len(swot["lg"].get("strengths", [])),
        len(swot["lg"].get("weaknesses", [])),
        len(swot["lg"].get("opportunities", [])),
        len(swot["lg"].get("threats", [])),
    ]
    catl_counts = [
        len(swot["catl"].get("strengths", [])),
        len(swot["catl"].get("weaknesses", [])),
        len(swot["catl"].get("opportunities", [])),
        len(swot["catl"].get("threats", [])),
    ]
    x = np.arange(len(labels))
    width = 0.35
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(x - width / 2, lg_counts, width, label="LGES", color="#2ca02c")
    ax.bar(x + width / 2, catl_counts, width, label="CATL", color="#d62728")
    ax.set_title("SWOT Item Counts")
    ax.set_ylabel("Count")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()
    return _save_chart(fig, output_dir / "swot_counts.png")


def key_metrics_chart(state: WorkflowState, output_dir: Path) -> str | None:
    lg_metrics = {m.get("label"): m for m in state["companies"]["lg"].get("analysis", {}).get("key_metrics", []) if m.get("value") is not None}
    catl_metrics = {m.get("label"): m for m in state["companies"]["catl"].get("analysis", {}).get("key_metrics", []) if m.get("value") is not None}
    shared = [label for label in lg_metrics if label in catl_metrics][:4]
    if not shared:
        return None
    lg_values = [float(lg_metrics[label]["value"]) for label in shared]
    catl_values = [float(catl_metrics[label]["value"]) for label in shared]
    x = np.arange(len(shared))
    width = 0.35
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(x - width / 2, lg_values, width, label="LGES", color="#4c78a8")
    ax.bar(x + width / 2, catl_values, width, label="CATL", color="#f58518")
    ax.set_title("Shared Quantitative Metrics")
    ax.set_ylabel("Value")
    ax.set_xticks(x)
    ax.set_xticklabels(shared, rotation=15, ha="right")
    ax.legend()
    return _save_chart(fig, output_dir / "key_metrics.png")


def generate_charts(state: WorkflowState, output_dir: Path) -> Dict[str, str]:
    chart_paths: Dict[str, str] = {}
    chart_paths["criterion_coverage"] = criterion_coverage_chart(state, output_dir)
    swot_path = swot_count_chart(state, output_dir)
    if swot_path:
        chart_paths["swot_counts"] = swot_path
    metrics_path = key_metrics_chart(state, output_dir)
    if metrics_path:
        chart_paths["key_metrics"] = metrics_path
    return chart_paths
