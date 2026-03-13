from __future__ import annotations

import json
import math
import os
from dataclasses import dataclass
from typing import List

from app.core.config import settings


def _ensure_vector_store_dir() -> str:
    path = settings.VECTOR_STORE_PATH
    os.makedirs(path, exist_ok=True)
    return path


@dataclass
class VectorDocument:
    section_id: int
    label_id: int
    drug_id: int
    country_code: str
    heading: str
    content: str
    embedding: list[float]


class VectorStore:
    def __init__(self) -> None:
        self._docs: list[VectorDocument] = []
        _ensure_vector_store_dir()

    def load(self) -> None:
        path = os.path.join(settings.VECTOR_STORE_PATH, "vectors.jsonl")
        if not os.path.exists(path):
            self._docs = []
            self._matrix = None
            return
        docs: list[VectorDocument] = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                data = json.loads(line)
                docs.append(
                    VectorDocument(
                        section_id=data["section_id"],
                        label_id=data["label_id"],
                        drug_id=data["drug_id"],
                        country_code=data["country_code"],
                        heading=data["heading"],
                        content=data["content"],
                        embedding=data["embedding"],
                    )
                )
        self._docs = docs

    def save(self) -> None:
        path = os.path.join(settings.VECTOR_STORE_PATH, "vectors.jsonl")
        with open(path, "w", encoding="utf-8") as f:
            for d in self._docs:
                f.write(
                    json.dumps(
                        {
                            "section_id": d.section_id,
                            "label_id": d.label_id,
                            "drug_id": d.drug_id,
                            "country_code": d.country_code,
                            "heading": d.heading,
                            "content": d.content,
                            "embedding": d.embedding,
                        }
                    )
                    + "\n"
                )

    @property
    def document_count(self) -> int:
        return len(self._docs)

    def rebuild_from_rows(self, rows: list[dict]) -> None:
        def embed(text: str) -> list[float]:
            text = (text or "")[:512]
            vec = [0.0] * 26
            for ch in text.lower():
                if "a" <= ch <= "z":
                    idx = ord(ch) - ord("a")
                    vec[idx] += 1.0
            norm = math.sqrt(sum(v * v for v in vec))
            if norm > 0:
                vec = [v / norm for v in vec]
            return vec

        docs: list[VectorDocument] = []
        for row in rows:
            emb = embed(row["content"])
            docs.append(
                VectorDocument(
                    section_id=row["section_id"],
                    label_id=row["label_id"],
                    drug_id=row["drug_id"],
                    country_code=row["country_code"],
                    heading=row["heading"],
                    content=row["content"],
                    embedding=emb,
                )
            )

        self._docs = docs
        self.save()

    def search(self, query: str, top_k: int = 5) -> List[VectorDocument]:
        if not self._docs:
            return []

        def embed_query(text: str) -> list[float]:
            text = (text or "")[:512]
            vec = [0.0] * 26
            for ch in text.lower():
                if "a" <= ch <= "z":
                    idx = ord(ch) - ord("a")
                    vec[idx] += 1.0
            norm = math.sqrt(sum(v * v for v in vec))
            if norm > 0:
                vec = [v / norm for v in vec]
            return vec

        q_vec = embed_query(query)

        def cosine(a: list[float], b: list[float]) -> float:
            return sum(x * y for x, y in zip(a, b))

        scored = [(cosine(d.embedding, q_vec), d) for d in self._docs]
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [d for _, d in scored[:top_k]]


vector_store = VectorStore()

