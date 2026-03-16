from typing import Any, List

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import ActivityLog
from app.services.vector_service import vector_store


router = APIRouter()


class SemanticSearchRequest(BaseModel):
    query: str
    top_k: int = 5


@router.post("/semantic")
async def semantic_search(
    body: SemanticSearchRequest, 
    db: AsyncSession = Depends(get_db)
) -> List[dict[str, Any]]:
    results = vector_store.search(body.query, top_k=body.top_k)
    
    # Log the search activity
    new_log = ActivityLog(
        type="search",
        title=f"Semantic Search: '{body.query}'",
        subtitle=f"Queried {len(results)} relevant section embeddings",
        meta={"query": body.query}
    )
    db.add(new_log)
    await db.commit()
    
    return [
        {
            "section_id": d.section_id,
            "label_id": d.label_id,
            "drug_id": d.drug_id,
            "country_code": d.country_code,
            "heading": d.heading,
            "content": d.content,
            "drug_name": d.drug_name,
            "brand_name": d.brand_name
        }
        for d in results
    ]

