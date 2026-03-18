from __future__ import annotations

import json
from typing import Iterable

from qdrant_client import QdrantClient


QDRANT_URL = "http://localhost:6333"
COLLECTIONS = [
    "battery_market_market",
    "battery_market_lg",
    "battery_market_catl",
]


def format_list(values: Iterable[str], limit: int = 5) -> str:
    values = [str(v) for v in values if v]
    if not values:
        return "-"
    if len(values) <= limit:
        return ", ".join(values)
    return ", ".join(values[:limit]) + f" ... (+{len(values) - limit})"


def main() -> None:
    client = QdrantClient(url=QDRANT_URL, check_compatibility=False)

    print(f"Qdrant URL: {QDRANT_URL}")
    print()

    for name in COLLECTIONS:
        count = client.count(name).count
        print(f"=== {name} ===")
        print(f"points: {count}")

        points, _ = client.scroll(
            collection_name=name,
            limit=3,
            with_payload=True,
            with_vectors=False,
        )

        if not points:
            print("sample: <empty>")
            print()
            continue

        for idx, point in enumerate(points, start=1):
            payload = point.payload or {}
            metadata = payload.get("metadata", {})
            page_content = payload.get("page_content", "")
            data = metadata if metadata else payload
            print(f"[sample {idx}]")
            print(f"  chunk_id: {data.get('chunk_id', '-')}")
            print(f"  source_id: {data.get('source_id', '-')}")
            print(f"  title: {data.get('title', '-')}")
            print(f"  publisher: {data.get('publisher', '-')}")
            print(f"  date: {data.get('date', '-')}")
            print(f"  company_scope: {data.get('company_scope', '-')}")
            print(f"  source_type: {data.get('source_type', '-')}")
            print(f"  criterion_tags: {format_list(data.get('criterion_tags', []))}")
            print(f"  sentiment_side: {data.get('sentiment_side', '-')}")
            excerpt = (data.get("excerpt") or data.get("content") or page_content or "").replace("\n", " ").strip()
            print(f"  excerpt: {excerpt[:180] if excerpt else '-'}")
        print()


if __name__ == "__main__":
    main()
