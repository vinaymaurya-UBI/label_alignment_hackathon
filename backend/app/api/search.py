from typing import Any, List

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.services.vector_service import vector_store


router = APIRouter()


class SemanticSearchRequest(BaseModel):
    query: str
    top_k: int = 5


@router.post("/semantic")
def semantic_search(body: SemanticSearchRequest) -> List[dict[str, Any]]:
    results = vector_store.search(body.query, top_k=body.top_k)
    return [
        {
            "section_id": d.section_id,
            "label_id": d.label_id,
            "drug_id": d.drug_id,
            "country_code": d.country_code,
            "heading": d.heading,
            "content": d.content,
        }
        for d in results
    ]

