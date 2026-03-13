"""
Query Interface for Drug Label Data
Test semantic search and data retrieval
"""

import asyncio
import logging
from typing import List
from app.database import AsyncSessionLocal
from app.models import Drug, DrugLabel, LabelSection, RegulatoryAuthority
from app.vector_store import VectorStore
from sqlalchemy import select, or_

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def list_all_drugs():
    """List all drugs in the database."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Drug))
        drugs = result.scalars().all()

        print(f"\n{'='*60}")
        print(f"DRUGS IN DATABASE ({len(drugs)} total)")
        print(f"{'='*60}\n")

        for drug in drugs:
            print(f"• {drug.generic_name}")
            if drug.brand_name:
                print(f"  Brand: {drug.brand_name}")
            print(f"  Manufacturer: {drug.manufacturer}")
            if drug.therapeutic_area:
                print(f"  Therapeutic Area: {drug.therapeutic_area}")
            print()

    return drugs


async def get_drug_sections(drug_name: str):
    """Get all sections for a specific drug."""
    async with AsyncSessionLocal() as session:
        # Find drug
        result = await session.execute(
            select(Drug).where(Drug.generic_name.ilike(f"%{drug_name}%"))
        )
        drug = result.scalar_one_or_none()

        if not drug:
            print(f"Drug '{drug_name}' not found")
            return

        print(f"\n{'='*60}")
        print(f"SECTIONS FOR: {drug.generic_name} ({drug.brand_name})")
        print(f"{'='*60}\n")

        # Get labels for this drug
        result = await session.execute(
            select(DrugLabel, RegulatoryAuthority)
            .join(RegulatoryAuthority, DrugLabel.authority_id == RegulatoryAuthority.id)
            .where(DrugLabel.drug_id == drug.id)
        )
        labels = result.all()

        for label, authority in labels:
            print(f"\n[{authority.country_name}]")
            print(f"Label Version: {label.version}")
            print(f"Effective Date: {label.effective_date}")

            # Get sections
            result = await session.execute(
                select(LabelSection)
                .where(LabelSection.label_id == label.id)
                .order_by(LabelSection.section_order)
            )
            sections = result.scalars().all()

            print(f"Sections ({len(sections)}):")
            for section in sections:
                content_preview = section.content[:100] + "..." if len(section.content) > 100 else section.content
                print(f"\n  ▸ {section.section_name}")
                print(f"    {content_preview}")


async def semantic_search(query: str, k: int = 5):
    """Perform semantic search on label sections."""
    print(f"\n{'='*60}")
    print(f"SEMANTIC SEARCH: '{query}'")
    print(f"{'='*60}\n")

    # Load vector store
    vector_store = VectorStore()
    vector_store.load()

    if vector_store.document_count == 0:
        print("No documents in vector store. Run main.py first.")
        return

    # Search
    results = vector_store.search(query, k=k)

    print(f"Found {len(results)} results:\n")

    for i, result in enumerate(results, 1):
        metadata = result.get("metadata", {})
        similarity = result.get("similarity", 0)

        print(f"{i}. [Similarity: {similarity:.4f}]")
        print(f"   Drug: {metadata.get('drug_name')} ({metadata.get('brand_name')})")
        print(f"   Manufacturer: {metadata.get('manufacturer')}")
        print(f"   Country: {metadata.get('country')}")
        print(f"   Section: {metadata.get('section_name')}")
        print(f"   Content Preview: {result['text'][:200]}...")
        print()


async def compare_drugs(drug_names: List[str]):
    """Compare sections between multiple drugs."""
    print(f"\n{'='*60}")
    print(f"DRUG COMPARISON: {', '.join(drug_names)}")
    print(f"{'='*60}\n")

    async with AsyncSessionLocal() as session:
        drugs = []
        for name in drug_names:
            result = await session.execute(
                select(Drug).where(Drug.generic_name.ilike(f"%{name}%"))
            )
            drug = result.scalar_one_or_none()
            if drug:
                drugs.append(drug)

        if len(drugs) < 2:
            print(f"Need at least 2 drugs to compare. Found: {len(drugs)}")
            return

        # Get sections for each drug
        all_sections = {}
        for drug in drugs:
            result = await session.execute(
                select(DrugLabel)
                .where(DrugLabel.drug_id == drug.id)
            )
            labels = result.scalars().all()

            drug_sections = {}
            for label in labels:
                result = await session.execute(
                    select(LabelSection)
                    .where(LabelSection.label_id == label.id)
                )
                sections = result.scalars().all()
                for section in sections:
                    if section.section_name not in drug_sections:
                        drug_sections[section.section_name] = []
                    drug_sections[section.section_name].append(section.content)

            all_sections[drug.generic_name] = drug_sections

        # Find common sections
        all_section_names = set()
        for sections in all_sections.values():
            all_section_names.update(sections.keys())

        # Compare sections
        for section_name in sorted(all_section_names):
            print(f"\n▸ {section_name}")
            print("-" * 50)

            for drug_name, sections in all_sections.items():
                if section_name in sections:
                    content = sections[section_name][0]
                    preview = content[:150] + "..." if len(content) > 150 else content
                    print(f"\n  {drug_name}:")
                    print(f"  {preview}")
                else:
                    print(f"\n  {drug_name}: [NOT FOUND]")
            print()


async def main():
    """Main menu for querying data."""
    print("\n" + "="*60)
    print("DRUG LABEL ALIGNMENT PLATFORM - QUERY INTERFACE")
    print("="*60)

    while True:
        print("\nOptions:")
        print("1. List all drugs")
        print("2. View sections for a drug")
        print("3. Semantic search")
        print("4. Compare drugs")
        print("5. Exit")

        choice = input("\nSelect option (1-5): ").strip()

        if choice == "1":
            await list_all_drugs()

        elif choice == "2":
            drug_name = input("Enter drug name (e.g., remdesivir): ").strip()
            if drug_name:
                await get_drug_sections(drug_name)

        elif choice == "3":
            query = input("Enter search query (e.g., 'dosage for renal impairment'): ").strip()
            if query:
                k = input("Number of results (default 5): ").strip()
                k = int(k) if k.isdigit() else 5
                await semantic_search(query, k)

        elif choice == "4":
            drugs_input = input("Enter drug names separated by comma (e.g., remdesivir,sofosbuvir): ").strip()
            if drugs_input:
                drug_names = [d.strip() for d in drugs_input.split(",")]
                await compare_drugs(drug_names)

        elif choice == "5":
            print("\nGoodbye!")
            break

        else:
            print("\nInvalid option. Please try again.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
