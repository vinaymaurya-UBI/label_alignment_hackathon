"""
Main Entry Point - Fetch and Store FDA Drug Data
Run this script to:
1. Initialize SQLite database
2. Fetch drug data from FDA
3. Store in database
4. Create embeddings and store in FAISS
"""

import asyncio
import logging
from pathlib import Path
from typing import List, Dict
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from app.database import engine, Base, AsyncSessionLocal
from app.models import Drug, RegulatoryAuthority, DrugLabel, LabelSection
from app.fda_client import fetch_sample_drugs
from app.vector_store import VectorStore


async def init_database():
    """Initialize database tables and seed regulatory authorities."""
    logger.info("Initializing database...")

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed regulatory authorities
    async with AsyncSessionLocal() as session:
        # Check if already seeded
        from sqlalchemy import select
        result = await session.execute(select(RegulatoryAuthority))
        if result.first():
            logger.info("Regulatory authorities already seeded")
            return

        # Add FDA authority
        fda = RegulatoryAuthority(
            country_code="US",
            country_name="United States",
            authority_name="U.S. Food and Drug Administration",
            api_endpoint="https://api.fda.gov/drug/label.json",
            data_source_type="API",
            is_active=True,
            meta={"rate_limit": 1000, "authentication": "API_KEY"}
        )
        session.add(fda)
        await session.commit()

        logger.info("Regulatory authorities seeded")


async def save_drug_to_db(session, drug_info: Dict, authority_id: str) -> Drug:
    """
    Save drug information to database.

    Args:
        session: Database session
        drug_info: Structured drug information from FDA
        authority_id: Regulatory authority ID

    Returns:
        Drug model instance
    """
    from sqlalchemy import select

    # Check if drug already exists
    result = await session.execute(
        select(Drug).where(
            Drug.generic_name == drug_info.get("generic_name"),
            Drug.manufacturer == drug_info.get("manufacturer")
        )
    )
    existing_drug = result.first()

    if existing_drug:
        logger.debug(f"Drug already exists: {drug_info.get('generic_name')}")
        return existing_drug[0]

    # Create new drug
    drug = Drug(
        generic_name=drug_info.get("generic_name") or "Unknown",
        brand_name=drug_info.get("brand_name"),
        manufacturer=drug_info.get("manufacturer") or "Unknown",
        active_ingredient=drug_info.get("active_ingredient") or drug_info.get("generic_name") or "Unknown",
        therapeutic_area=drug_info.get("therapeutic_area"),
        meta={
            "product_ndc": drug_info.get("product_ndc"),
            "spl_id": drug_info.get("spl_id"),
            "application_number": drug_info.get("application_number")
        }
    )
    session.add(drug)
    await session.flush()
    await session.refresh(drug)

    logger.info(f"Created drug: {drug.generic_name} ({drug.brand_name})")
    return drug


async def save_label_to_db(session, drug_id: str, authority_id: str, drug_info: Dict) -> DrugLabel:
    """
    Save drug label to database.

    Args:
        session: Database session
        drug_id: Drug ID
        authority_id: Regulatory authority ID
        drug_info: Structured drug information

    Returns:
        DrugLabel model instance
    """
    from sqlalchemy import select
    import hashlib

    # Create hash of raw content for deduplication
    content_str = str(drug_info.get("sections", {}))
    content_hash = hashlib.sha256(content_str.encode()).hexdigest()

    # Check if label already exists
    result = await session.execute(
        select(DrugLabel).where(
            DrugLabel.drug_id == drug_id,
            DrugLabel.authority_id == authority_id,
            DrugLabel.hash_sha256 == content_hash
        )
    )
    existing_label = result.first()

    if existing_label:
        logger.debug(f"Label already exists for drug {drug_id}")
        return existing_label[0]

    # Create new label
    from datetime import datetime

    # Parse effective_date
    effective_date = None
    if drug_info.get("effective_date"):
        try:
            effective_date = datetime.fromisoformat(drug_info.get("effective_date").replace('Z', '+00:00'))
        except:
            pass

    if not effective_date:
        try:
            effective_date = datetime.fromisoformat(drug_info.get("fetched_at").replace('Z', '+00:00'))
        except:
            effective_date = datetime.utcnow()

    label = DrugLabel(
        drug_id=drug_id,
        authority_id=authority_id,
        version=1,
        label_type="PACKAGE_INSERT",
        effective_date=effective_date,
        raw_content=content_str,
        hash_sha256=content_hash,
        meta=drug_info.get("raw_data", {})
    )
    session.add(label)
    await session.flush()
    await session.refresh(label)

    # Save sections
    sections = drug_info.get("sections", {})
    for section_name, content in sections.items():
        if content:
            section = LabelSection(
                label_id=label.id,
                section_name=section_name,
                section_order=len(sections),
                content=content,
                normalized_content=content.strip()
            )
            session.add(section)

    await session.commit()
    logger.info(f"Created label with {len(sections)} sections for drug {drug_id}")
    return label


async def create_embeddings(vector_store: VectorStore, session):
    """
    Create embeddings for all label sections and store in FAISS.

    Args:
        vector_store: FAISS vector store instance
        session: Database session
    """
    from sqlalchemy import select

    logger.info("Creating embeddings for label sections...")

    # Get all sections
    result = await session.execute(select(LabelSection))
    sections = result.scalars().all()

    if not sections:
        logger.warning("No sections found to create embeddings")
        return

    # Prepare documents for embedding
    documents = []
    for section in sections:
        # Get section context
        label_result = await session.execute(
            select(DrugLabel, Drug, RegulatoryAuthority)
            .join(Drug, DrugLabel.drug_id == Drug.id)
            .join(RegulatoryAuthority, DrugLabel.authority_id == RegulatoryAuthority.id)
            .where(DrugLabel.id == section.label_id)
        )
        label_data = label_result.first()

        if label_data:
            label, drug, authority = label_data

            # Create enhanced text for embedding
            text = f"""
            Drug: {drug.generic_name} ({drug.brand_name})
            Manufacturer: {drug.manufacturer}
            Country: {authority.country_name}
            Section: {section.section_name}
            Content: {section.content}
            """

            documents.append({
                "id": f"section_{section.id}",
                "text": text.strip(),
                "metadata": {
                    "section_id": section.id,
                    "label_id": section.label_id,
                    "drug_id": drug.id,
                    "drug_name": drug.generic_name,
                    "brand_name": drug.brand_name,
                    "manufacturer": drug.manufacturer,
                    "country": authority.country_code,
                    "section_name": section.section_name
                }
            })

    # Add to vector store
    if documents:
        doc_ids = vector_store.add_documents(documents)
        logger.info(f"Created embeddings for {len(doc_ids)} sections")

        # Save vector store
        vector_store.save()


async def main():
    """Main function to fetch and store drug data."""
    logger.info("=" * 60)
    logger.info("Drug Label Alignment Platform - Data Fetcher")
    logger.info("=" * 60)

    try:
        # Step 1: Initialize database
        await init_database()
        logger.info("✓ Database initialized")

        # Step 2: Fetch FDA drug data
        api_key = os.getenv("FDA_API_KEY")
        logger.info(f"Fetching drug data from FDA...")
        drugs_data = await fetch_sample_drugs(api_key=api_key)
        logger.info(f"✓ Fetched {len(drugs_data)} drugs from FDA")

        # Step 3: Get FDA authority ID
        async with AsyncSessionLocal() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(RegulatoryAuthority).where(RegulatoryAuthority.country_code == "US")
            )
            fda_authority = result.first()
            if not fda_authority:
                raise Exception("FDA authority not found in database")
            authority_id = fda_authority[0].id

            # Step 4: Save drugs and labels to database
            logger.info("Saving drugs and labels to database...")
            for drug_info in drugs_data:
                try:
                    drug = await save_drug_to_db(session, drug_info, authority_id)
                    await save_label_to_db(session, drug.id, authority_id, drug_info)
                except Exception as e:
                    logger.error(f"Error saving drug: {e}")
                    continue

            await session.commit()
            logger.info(f"✓ Saved {len(drugs_data)} drugs to database")

            # Step 5: Create embeddings
            vector_store = VectorStore()
            await create_embeddings(vector_store, session)
            logger.info(f"✓ Created embeddings for {vector_store.document_count} sections")

            # Step 6: Summary
            logger.info("=" * 60)
            logger.info("SUMMARY")
            logger.info("=" * 60)

            # Count drugs
            from sqlalchemy import func
            drug_count = await session.execute(select(func.count()).select_from(Drug))
            logger.info(f"Total drugs in database: {drug_count.scalar()}")

            # Count labels
            label_count = await session.execute(select(func.count()).select_from(DrugLabel))
            logger.info(f"Total labels in database: {label_count.scalar()}")

            # Count sections
            section_count = await session.execute(select(func.count()).select_from(LabelSection))
            logger.info(f"Total sections in database: {section_count.scalar()}")

            # Show sample drugs
            result = await session.execute(select(Drug).limit(10))
            drugs = result.scalars().all()

            logger.info("\nSample drugs:")
            for drug in drugs:
                logger.info(f"  - {drug.generic_name} ({drug.brand_name}) by {drug.manufacturer}")

            logger.info("\n✓ Data fetching complete!")
            logger.info(f"✓ Vector store saved with {vector_store.document_count} embeddings")
            logger.info("\nYou can now run queries against the data.")

    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise

    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
