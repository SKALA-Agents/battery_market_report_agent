from __future__ import annotations

import hashlib
import os
import re
from collections import Counter
from datetime import datetime, timezone
from functools import lru_cache
from typing import Dict, Iterable, List, Optional

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from tavily import TavilyClient

from .config import get_settings
from .state import ANALYSIS_CRITERIA, RetrievalDiagnostics, RetrievalStatus, SourceMeta, WebSearchRecord


COMPANY_LABELS = {
    "lg": "LG Energy Solution",
    "catl": "CATL",
    "market": "Battery Market",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def get_chat_model() -> ChatOpenAI:
    settings = get_settings()
    require_env("OPENAI_API_KEY")
    return ChatOpenAI(model=settings.openai_model, temperature=0)


@lru_cache(maxsize=1)
def get_embedding_model() -> HuggingFaceEmbeddings:
    settings = get_settings()
    return HuggingFaceEmbeddings(
        model_name=settings.embedding_model,
        model_kwargs={"device": settings.embedding_device},
        encode_kwargs={"normalize_embeddings": True},
    )


def structured_llm(schema):
    return get_chat_model().with_structured_output(schema, method="function_calling")


def tavily_enabled() -> bool:
    return bool(os.getenv("TAVILY_API_KEY"))


class TavilySearchTool:
    def __init__(self) -> None:
        self.client: Optional[TavilyClient] = None
        if tavily_enabled():
            self.client = TavilyClient(api_key=require_env("TAVILY_API_KEY"))

    def search(self, query: str, max_results: int = 5) -> List[dict]:
        if self.client is None:
            return []
        response = self.client.search(
            query=query,
            max_results=max_results,
            search_depth="advanced",
            include_answer=False,
            include_raw_content=False,
        )
        return response.get("results", [])


class InMemoryFaissRetriever:
    def __init__(self) -> None:
        self._vectorstore: Optional[FAISS] = None

    def build_index(self, documents: Iterable[Document]) -> None:
        docs = [doc for doc in documents if doc.page_content.strip()]
        if not docs:
            self._vectorstore = None
            return
        self._vectorstore = FAISS.from_documents(docs, get_embedding_model())

    def search(self, query: str, k: int = 5) -> List[Document]:
        if self._vectorstore is None:
            return []
        return self._vectorstore.similarity_search(query, k=k)


def make_source_id(title: str, url: str) -> str:
    digest = hashlib.md5(f"{title}|{url}".encode("utf-8")).hexdigest()[:12]
    return f"src_{digest}"


def make_chunk_id(source_id: str, index: int) -> str:
    return f"{source_id}_chunk_{index}"


def extract_numeric_facts(text: str, limit: int = 12) -> List[str]:
    tokens = re.findall(r"\b[\d,.%]+(?:[A-Za-z]+)?\b", text)
    return tokens[:limit]


def extract_year(text: str) -> str:
    match = re.search(r"(20\d{2})", text)
    return match.group(1) if match else ""


def infer_region_tags(text: str) -> List[str]:
    haystack = text.lower()
    tags = []
    for token, label in [("north america", "us"), ("u.s.", "us"), ("europe", "eu"), ("eu", "eu"), ("china", "china"), ("global", "global")]:
        if token in haystack and label not in tags:
            tags.append(label)
    return tags or ["global"]


def map_tags_to_criteria(tags: List[str]) -> List[str]:
    text = " ".join(tags).lower()
    criteria = []
    mapping = {
        "포트폴리오 다양성": ["portfolio", "ess", "ev", "sodium_ion", "battery_swapping", "product_strategy"],
        "기술 경쟁력": ["technology", "solid_state", "lfp", "sodium_ion", "fast_charging", "prismatic", "ctp"],
        "시장 대응력": ["market", "operations", "risk_response", "commercialization", "policy"],
        "공급망 전략": ["supply_chain", "critical_minerals", "nickel", "lithium", "upstream", "vertical_integration", "localization"],
        "고객/파트너 구조": ["oem", "partnership", "service_network", "ecosystem"],
        "글로벌 확장성": ["north_america", "global_expansion", "regional_competition", "infrastructure", "zero_carbon"],
        "리스크 대응력": ["risk", "safety", "recycling", "compliance", "pressure", "criticism", "regulation_update"],
    }
    for criterion, keys in mapping.items():
        if any(key in text for key in keys):
            criteria.append(criterion)
    return criteria


def infer_sentiment_side(tags: List[str], text: str) -> str:
    haystack = " ".join(tags).lower() + " " + text.lower()
    if any(word in haystack for word in ["risk", "pressure", "criticism", "compliance", "safety", "recycling", "threat", "challenge"]):
        return "risk"
    if any(word in haystack for word in ["growth", "opportunity", "expansion", "breakthrough"]):
        return "positive"
    return "neutral"


def documents_from_sources(sources: List[SourceMeta]) -> List[Document]:
    docs = []
    for source in sources:
        content = source.get("excerpt", "")
        if not content:
            continue
        docs.append(
            Document(
                page_content=content,
                metadata=dict(source),
            )
        )
    return docs


def merge_sources(existing: List[SourceMeta], new_sources: List[SourceMeta]) -> List[SourceMeta]:
    merged: Dict[str, SourceMeta] = {item["source_id"]: item for item in existing}
    for item in new_sources:
        merged[item["source_id"]] = item
    return list(merged.values())


def source_registry_update(sources: List[SourceMeta]) -> Dict[str, SourceMeta]:
    return {source["source_id"]: source for source in sources}


def filter_company_sources(company: str, sources: List[SourceMeta]) -> List[SourceMeta]:
    company_terms = {
        "lg": ["lg energy solution", "lg에너지솔루션", "lges"],
        "catl": ["catl", "宁德时代"],
    }
    rival = "catl" if company == "lg" else "lg"
    own_terms = company_terms.get(company, [])
    rival_terms = company_terms.get(rival, [])
    filtered = []
    for source in sources:
        haystack = f"{source['title']} {source['excerpt']}".lower()
        own_hit = any(term.lower() in haystack for term in own_terms)
        rival_hit = any(term.lower() in haystack for term in rival_terms)
        if rival_hit and not own_hit:
            continue
        filtered.append(source)
    return filtered


def normalize_search_results(raw_results: List[dict], company_scope: str) -> List[SourceMeta]:
    normalized: List[SourceMeta] = []
    for item in raw_results:
        title = item.get("title") or "Untitled"
        url = item.get("url") or ""
        content = item.get("content") or ""
        excerpt = content[:1500]
        source_id = make_source_id(title, url)
        year = extract_year(" ".join([title, url, excerpt]))
        source_type = "news"
        domain = item.get("domain") or ""
        if any(key in domain for key in ["gov", "europa", "iea"]):
            source_type = "policy"
        if any(key in domain for key in ["lgensol.com", "catl.com"]):
            source_type = "official_company"
        tags = []
        criteria_tags = map_tags_to_criteria(tags + [title, excerpt])
        normalized.append(
            SourceMeta(
                source_id=source_id,
                source_type=source_type,
                title=title,
                url=url,
                date=year,
                publisher=domain,
                excerpt=excerpt,
                numeric_facts=extract_numeric_facts(content),
                reliability_note="web_search",
                company_scope=company_scope,
                criterion_tags=criteria_tags,
                sentiment_side=infer_sentiment_side(tags, excerpt),
                region_tags=infer_region_tags(" ".join([title, excerpt])),
            )
        )
    return normalized


def evaluate_retrieval(sources: List[SourceMeta], required_scope: str) -> tuple[RetrievalStatus, RetrievalDiagnostics]:
    all_criteria = set()
    stale_sources = []
    type_counter: Counter = Counter()
    has_counter_evidence = False
    for source in sources:
        all_criteria.update(source.get("criterion_tags", []))
        if source.get("date") and source["date"].isdigit() and int(source["date"]) < 2024:
            stale_sources.append(source["source_id"])
        type_counter[source.get("source_type", "unknown")] += 1
        if source.get("sentiment_side") in {"risk", "critical"}:
            has_counter_evidence = True
        if any(tag in source.get("criterion_tags", []) for tag in ["리스크 대응력"]):
            has_counter_evidence = True

    missing = [criterion for criterion in ANALYSIS_CRITERIA if criterion not in all_criteria]
    coverage_ok = len(ANALYSIS_CRITERIA) - len(missing) >= 5 if required_scope != "market" else len(sources) >= 4
    freshness_ok = len(stale_sources) <= max(1, len(sources) // 2)
    diversity_ok = len(type_counter) >= (2 if required_scope == "market" else 1)
    counter_evidence_ok = has_counter_evidence or required_scope == "market"

    reasons = []
    if not coverage_ok:
        reasons.append("자료 부족")
    if not freshness_ok:
        reasons.append("자료 노후")
    if not diversity_ok:
        reasons.append("출처 다양성 부족")
    if not counter_evidence_ok:
        reasons.append("반증 부족")

    diagnostics = RetrievalDiagnostics(
        coverage_ok=coverage_ok,
        freshness_ok=freshness_ok,
        diversity_ok=diversity_ok,
        counter_evidence_ok=counter_evidence_ok,
        missing_criteria=missing,
        stale_sources=stale_sources,
        source_type_distribution=dict(type_counter),
        notes=reasons.copy(),
    )
    status = RetrievalStatus(
        sufficient=not reasons,
        used_web_search=False,
        reason=reasons.copy(),
        last_updated_at=now_iso(),
    )
    return status, diagnostics


def mark_web_search(status: RetrievalStatus, reasons: List[str]) -> RetrievalStatus:
    updated = dict(status)
    updated["used_web_search"] = True
    updated["reason"] = list(dict.fromkeys(status.get("reason", []) + reasons))
    updated["last_updated_at"] = now_iso()
    return RetrievalStatus(**updated)


def make_web_search_record(query: str, reasons: List[str], added_source_ids: List[str]) -> WebSearchRecord:
    return WebSearchRecord(
        query=query,
        trigger_reason=reasons,
        added_source_ids=added_source_ids,
        executed_at=now_iso(),
    )


def retrieve_evidence_snippets(sources: List[SourceMeta], queries: List[str], k: int = 4) -> List[str]:
    retriever = InMemoryFaissRetriever()
    retriever.build_index(documents_from_sources(sources))
    snippets: List[str] = []
    seen = set()
    for query in queries:
        for doc in retriever.search(query, k=k):
            source_id = doc.metadata.get("source_id", "")
            snippet = f"[{source_id}] {doc.page_content}"
            if snippet in seen:
                continue
            seen.add(snippet)
            snippets.append(snippet)
    return snippets[:20]
