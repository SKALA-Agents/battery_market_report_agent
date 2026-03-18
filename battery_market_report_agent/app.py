from __future__ import annotations

import argparse
import os
import warnings
from pathlib import Path

from urllib3.exceptions import NotOpenSSLWarning

from .charts import generate_charts
from .config import get_settings
from .formatter import render_markdown_report, write_markdown_report, write_state_snapshot
from .graph import build_graph
from .state import make_initial_state
from .vector_db import get_qdrant_client, ingest_static_corpus


warnings.filterwarnings("ignore", category=NotOpenSSLWarning)
warnings.filterwarnings("ignore", message="Pydantic serializer warnings")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", default=None, help="사용자 질의")
    parser.add_argument("--force-reingest", action="store_true", help="정적 RAG 데이터를 다시 적재")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    settings = get_settings()
    mpl_dir = settings.project_root / ".mplconfig"
    mpl_dir.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("MPLCONFIGDIR", str(mpl_dir))
    get_qdrant_client(settings).get_collections()
    ingest_static_corpus(force_recreate=args.force_reingest, settings=settings)

    initial_state = make_initial_state(args.query or settings.default_query)
    graph = build_graph()
    result = graph.invoke(initial_state)

    chart_paths = generate_charts(result, settings.charts_dir)
    result["chart_paths"] = chart_paths

    report_md = render_markdown_report(result, {key: f"charts/{Path(path).name}" for key, path in chart_paths.items()})
    report_path = settings.outputs_dir / "final_report.md"
    state_path = settings.outputs_dir / "final_state.json"
    write_markdown_report(report_path, report_md)
    write_state_snapshot(state_path, result)

    print(f"Report written to: {report_path}")
    print(f"State written to: {state_path}")


if __name__ == "__main__":
    main()
