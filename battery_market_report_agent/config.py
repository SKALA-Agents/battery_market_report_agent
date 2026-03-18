from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent.parent
PARENT_ROOT = PROJECT_ROOT.parent.parent

load_dotenv(PROJECT_ROOT / ".env")
load_dotenv(PARENT_ROOT / ".env")


@dataclass(frozen=True)
class Settings:
    project_root: Path = PROJECT_ROOT
    rag_data_dir: Path = PROJECT_ROOT / "rag_data"
    outputs_dir: Path = PROJECT_ROOT / "outputs"
    charts_dir: Path = PROJECT_ROOT / "outputs" / "charts"
    qdrant_url: str = os.getenv("QDRANT_URL", "http://localhost:6333")
    qdrant_collection_market: str = os.getenv("QDRANT_COLLECTION_MARKET", "battery_market_market")
    qdrant_collection_lg: str = os.getenv("QDRANT_COLLECTION_LG", "battery_market_lg")
    qdrant_collection_catl: str = os.getenv("QDRANT_COLLECTION_CATL", "battery_market_catl")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    embedding_model: str = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    default_query: str = (
        "글로벌 배터리 시장 변화 속에서 LG에너지솔루션과 CATL의 포트폴리오 다각화 전략을 비교 분석하고, "
        "LG에너지솔루션 관점의 실행 가능한 시사점을 도출해줘."
    )

    @property
    def collections(self) -> dict:
        return {
            "market": self.qdrant_collection_market,
            "lg": self.qdrant_collection_lg,
            "catl": self.qdrant_collection_catl,
        }


def get_settings() -> Settings:
    settings = Settings()
    settings.outputs_dir.mkdir(parents=True, exist_ok=True)
    settings.charts_dir.mkdir(parents=True, exist_ok=True)
    return settings
