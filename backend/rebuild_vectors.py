import asyncio
import sys
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models import LabelSection, DrugLabel, Drug, RegulatoryAuthority
from app.services.vector_service import vector_store

async def rebuild():
    print("Connecting to database...")
    async with AsyncSessionLocal() as db:
        print("Fetching all sections for indexing...")
        stmt = (
            select(LabelSection, DrugLabel, Drug, RegulatoryAuthority)
            .join(DrugLabel, LabelSection.label_id == DrugLabel.id)
            .join(Drug, DrugLabel.drug_id == Drug.id)
            .join(RegulatoryAuthority, DrugLabel.authority_id == RegulatoryAuthority.id)
        )
        result = await db.execute(stmt)
        rows = []
        for section, label, drug, auth in result.all():
            rows.append({
                "section_id": section.id,
                "label_id": label.id,
                "drug_id": drug.id,
                "country_code": auth.country_code,
                "heading": section.section_name,
                "content": section.content,
                "drug_name": drug.generic_name,
                "brand_name": drug.brand_name or "N/A"
            })
        
        print(f"Indexing {len(rows)} sections...")
        vector_store.rebuild_from_rows(rows)
        print("Vector store rebuild complete!")

if __name__ == "__main__":
    asyncio.run(rebuild())
