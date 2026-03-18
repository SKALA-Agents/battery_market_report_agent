from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Tuple

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest

from .config import Settings, get_settings
from .tools import (
    extract_numeric_facts,
    extract_year,
    get_embedding_model,
    infer_region_tags,
    infer_sentiment_side,
    make_chunk_id,
    make_source_id,
    map_tags_to_criteria,
)


def get_qdrant_client(settings: Settings | None = None) -> QdrantClient:
    settings = settings or get_settings()
    return QdrantClient(url=settings.qdrant_url, timeout=20, check_compatibility=False)


def ensure_collection(client: QdrantClient, collection_name: str, vector_size: int = 1536) -> None:
    if client.collection_exists(collection_name):
        return
    client.create_collection(
        collection_name=collection_name,
        vectors_config=rest.VectorParams(size=vector_size, distance=rest.Distance.COSINE),
    )


def collection_name_for_path(path: Path, settings: Settings) -> Tuple[str, str]:
    stem = path.stem.lower()
    if "battery_market" in stem:
        return settings.qdrant_collection_market, "market"
    if "lg" in stem:
        return settings.qdrant_collection_lg, "lg"
    return settings.qdrant_collection_catl, "catl"


def parse_source_pack(path: Path) -> List[Document]:
    text = path.read_text(encoding="utf-8")
    source_docs: List[Document] = []
    matches = list(re.finditer(r"^#### (.+)$", text, flags=re.MULTILINE))
    for index, match in enumerate(matches):
        title = match.group(1).strip()
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        block = text[start:end]
        url_match = re.search(r"Link:\s*\[(.*?)\]\((.*?)\)", block)
        url = url_match.group(2).strip() if url_match else ""
        tags = re.findall(r"- `([^`]+)`", block)
        bullet_lines = re.findall(r"^\s*-\s+(.*)$", block, flags=re.MULTILINE)
        excerpt = "\n".join(line.strip() for line in bullet_lines if not line.startswith("Link:"))
        source_id = make_source_id(title, url)
        metadata = {
            "source_id": source_id,
            "source_type": "official_company" if "lg" in path.stem.lower() or "catl" in path.stem.lower() else "industry_report",
            "title": title,
            "url": url,
            "date": extract_year(f"{title} {url} {excerpt}"),
            "publisher": re.sub(r"^www\.", "", re.sub(r"^https?://", "", url).split("/")[0]) if url else path.stem,
            "excerpt": excerpt,
            "numeric_facts": extract_numeric_facts(excerpt),
            "reliability_note": "static_rag_source_pack",
            "company_scope": "lg" if "lg" in path.stem.lower() else ("catl" if "catl" in path.stem.lower() else "market"),
            "criterion_tags": map_tags_to_criteria(tags + [excerpt, title]),
            "sentiment_side": infer_sentiment_side(tags, excerpt),
            "region_tags": infer_region_tags(f"{title} {excerpt}"),
        }
        source_docs.append(
            Document(
                page_content=f"{title}\n{excerpt}\nTags: {', '.join(tags)}",
                metadata=metadata,
            )
        )
    return source_docs


def split_documents(documents: List[Document], company_scope: str) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=900, chunk_overlap=120)
    chunks: List[Document] = []
    for source_doc in documents:
        for idx, chunk in enumerate(splitter.split_documents([source_doc])):
            chunk.metadata["chunk_id"] = make_chunk_id(source_doc.metadata["source_id"], idx)
            chunk.metadata["kb_type"] = company_scope
            chunk.metadata["company_scope"] = company_scope
            chunks.append(chunk)
    return chunks


def ingest_static_corpus(force_recreate: bool = False, settings: Settings | None = None) -> Dict[str, int]:
    settings = settings or get_settings()
    client = get_qdrant_client(settings)
    embeddings = get_embedding_model()
    ingested_counts: Dict[str, int] = {}

    for path in sorted(settings.rag_data_dir.glob("*.md")):
        collection_name, scope = collection_name_for_path(path, settings)
        if force_recreate and client.collection_exists(collection_name):
            client.delete_collection(collection_name)
        ensure_collection(client, collection_name)
        if client.count(collection_name).count > 0 and not force_recreate:
            ingested_counts[scope] = client.count(collection_name).count
            continue

        source_docs = parse_source_pack(path)
        chunks = split_documents(source_docs, scope)
        store = QdrantVectorStore(
            client=client,
            collection_name=collection_name,
            embedding=embeddings,
        )
        store.add_documents(chunks)
        ingested_counts[scope] = len(chunks)
    return ingested_counts


def retrieve_static(scope: str, queries: List[str], k: int = 6, settings: Settings | None = None) -> List[Document]:
    settings = settings or get_settings()
    client = get_qdrant_client(settings)
    collection_name = settings.collections[scope]
    ensure_collection(client, collection_name)
    store = QdrantVectorStore(
        client=client,
        collection_name=collection_name,
        embedding=get_embedding_model(),
    )
    docs: List[Document] = []
    seen = set()
    for query in queries:
        for doc in store.similarity_search(query, k=k):
            chunk_id = doc.metadata.get("chunk_id") or f"{doc.metadata.get('source_id')}:{len(docs)}"
            if chunk_id in seen:
                continue
            seen.add(chunk_id)
            docs.append(doc)
    return docs
