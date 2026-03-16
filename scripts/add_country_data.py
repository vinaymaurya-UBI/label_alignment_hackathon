"""
Add regulatory data from multiple countries for cross-country comparison.
This script now uses REAL data from regulatory authority websites and APIs,
replacing the previous mock/simulated data approach.

Data Sources:
- US: FDA openFDA API (live)
- JP: PMDA Website (web scraping)
- IN: CDSCO Portal (web scraping)
- GB: MHRA/EMC Database (web scraping)
- CA: Health Canada DPD (web scraping)
"""

import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import AsyncSessionLocal
from app.models import Drug, DrugLabel, RegulatoryAuthority
from app.services.ingestion_service import RegulatoryIngestionService
from sqlalchemy import select


async def check_existing_data():
    """Check what data already exists in the database."""
    async with AsyncSessionLocal() as session:
        # Count drugs
        drugs_result = await session.execute(select(Drug))
        drug_count = len(drugs_result.scalars().all())

        # Count labels by country
        labels_result = await session.execute(
            select(RegulatoryAuthority.country_code)
            .join(DrugLabel, DrugLabel.authority_id == RegulatoryAuthority.id)
        )
        countries = set(labels_result.scalars().all())

        print("\nExisting Data:")
        print(f"  - Drugs: {drug_count}")
        print(f"  - Countries with labels: {', '.join(sorted(countries)) if countries else 'None'}")

        return drug_count, countries


async def add_regulatory_authorities():
    """Add regulatory authorities to database."""
    authorities_data = {
        "US": {
            "country_code": "US",
            "country_name": "United States",
            "authority_name": "U.S. Food and Drug Administration (FDA)",
            "api_endpoint": "https://open.fda.gov/",
            "data_source_type": "API",
            "is_active": True
        },
        "JP": {
            "country_code": "JP",
            "country_name": "Japan",
            "authority_name": "Pharmaceuticals and Medical Devices Agency (PMDA)",
            "api_endpoint": "https://www.pmda.go.jp/",
            "data_source_type": "SCRAPER",
            "is_active": True
        },
        "IN": {
            "country_code": "IN",
            "country_name": "India",
            "authority_name": "Central Drugs Standard Control Organization (CDSCO)",
            "api_endpoint": "https://cdsco.gov.in/",
            "data_source_type": "SCRAPER",
            "is_active": True
        },
        "GB": {
            "country_code": "GB",
            "country_name": "United Kingdom",
            "authority_name": "Medicines and Healthcare products Regulatory Agency (MHRA)",
            "api_endpoint": "https://www.gov.uk/government/organisations/medicines-and-healthcare-products-regulatory-agency",
            "data_source_type": "SCRAPER",
            "is_active": True
        },
        "CA": {
            "country_code": "CA",
            "country_name": "Canada",
            "authority_name": "Health Canada",
            "api_endpoint": "https://www.canada.ca/en/health-canada",
            "data_source_type": "SCRAPER",
            "is_active": True
        }
    }

    async with AsyncSessionLocal() as session:
        # Check existing authorities
        result = await session.execute(select(RegulatoryAuthority))
        existing = {auth.country_code: auth for auth in result.scalars().all()}

        added_count = 0
        for country_code, data in authorities_data.items():
            if country_code not in existing:
                authority = RegulatoryAuthority(**data)
                session.add(authority)
                added_count += 1
                print(f"  [+] Added {data['country_name']} ({data['authority_name']})")

        if added_count > 0:
            await session.commit()
            print(f"\n[OK] Added {added_count} regulatory authorities")
        else:
            print("\n[OK] All regulatory authorities already exist")


async def ingest_from_regulatory_authorities(skip_existing: bool = True):
    """
    Ingest real drug label data from all regulatory authorities.

    Args:
        skip_existing: If True, skip drugs that already exist in database
    """
    print("\n" + "="*80)
    print("INGESTING REAL DATA FROM REGULATORY AUTHORITIES")
    print("="*80)
    print("\nData Sources:")
    print("  [US] openFDA API: https://open.fda.gov/")
    print("  [JP] PMDA Website: https://www.pmda.go.jp/")
    print("  [IN] CDSCO Portal: https://cdsco.gov.in/")
    print("  [GB] MHRA/EMC Database: https://www.medicines.org.uk/")
    print("  [CA] Health Canada DPD: https://health-products.canada.ca/")

    print(f"\nTarget Drugs: {len(RegulatoryIngestionService.TARGET_DRUGS)}")
    for drug in RegulatoryIngestionService.TARGET_DRUGS[:5]:
        print(f"  - {drug['brand']} ({drug['generic']})")
    print(f"  ... and {len(RegulatoryIngestionService.TARGET_DRUGS) - 5} more")

    print("\nStarting ingestion...")
    print("-" * 80)

    service = RegulatoryIngestionService()

    # Test connections
    print("\n[*] Testing connections to regulatory authorities...")
    connections = await service.test_all_connections()

    connected = sum(1 for success in connections.values() if success)
    print(f"\n[*] Connected to {connected}/{len(connections)} authorities")

    # Run ingestion
    print("\n[*] Ingesting drug data...")
    results = await service.ingest_all_drugs(skip_existing=skip_existing)

    # Print detailed summary
    print("\n" + "="*80)
    print("INGESTION COMPLETE - SUMMARY")
    print("="*80)
    print(f"\nOverall Results:")
    print(f"  Total drugs processed: {results['total_processed']}")
    print(f"  Successful: {results['successful']}")
    print(f"  Failed: {results['failed']}")

    print(f"\nBy Country:")
    for country, stats in sorted(results['by_country'].items()):
        success_rate = (stats['successful'] / (stats['successful'] + stats['failed']) * 100
                        if (stats['successful'] + stats['failed']) > 0 else 0)
        status = "[+]" if stats['successful'] > 0 else "[X]"
        print(f"  {status} {country}: {stats['successful']} successful, {stats['failed']} failed ({success_rate:.0f}%)")

    if results['errors']:
        print(f"\nErrors (first 10):")
        for error in results['errors'][:10]:
            print(f"  - {error['drug']}: {error['error']}")

    return results


async def show_coverage():
    """Show cross-country data coverage."""
    async with AsyncSessionLocal() as session:
        drugs_result = await session.execute(
            select(Drug).order_by(Drug.generic_name)
        )
        drugs = drugs_result.scalars().all()

        print("\n" + "="*80)
        print("CROSS-COUNTRY DATA COVERAGE")
        print("="*80)

        multi_country_drugs = []
        for drug in drugs:
            labels_result = await session.execute(
                select(RegulatoryAuthority.country_code)
                .join(DrugLabel, DrugLabel.authority_id == RegulatoryAuthority.id)
                .where(DrugLabel.drug_id == drug.id)
            )
            countries = set(labels_result.scalars().all())

            if len(countries) > 1:
                multi_country_drugs.append({
                    'drug': drug,
                    'countries': countries
                })

        print(f"\nDrugs with multi-country coverage: {len(multi_country_drugs)}\n")

        # Group by coverage
        coverage_groups = {}
        for item in multi_country_drugs:
            coverage = len(item['countries'])
            if coverage not in coverage_groups:
                coverage_groups[coverage] = []
            coverage_groups[coverage].append(item['drug'].brand_name or item['drug'].generic_name)

        for coverage in sorted(coverage_groups.keys(), reverse=True):
            drugs_list = coverage_groups[coverage][:5]  # First 5 drugs
            print(f"  {coverage} countries: {', '.join(drugs_list)}")
            if len(coverage_groups[coverage]) > 5:
                print(f"                  ... and {len(coverage_groups[coverage]) - 5} more")

        # Show detailed example
        if multi_country_drugs:
            example = multi_country_drugs[0]
            print(f"\nExample: {example['drug'].generic_name} ({example['drug'].brand_name})")
            print(f"   Coverage: {', '.join(sorted(example['countries']))}")

            # Show sections from one country
            labels_result = await session.execute(
                select(DrugLabel)
                .where(DrugLabel.drug_id == example['drug'].id)
                .limit(1)
            )
            label = labels_result.scalar_one_or_none()

            if label:
                from app.models import LabelSection
                sections_result = await session.execute(
                    select(LabelSection.section_name)
                    .where(LabelSection.label_id == label.id)
                    .order_by(LabelSection.section_order)
                )
                sections = sections_result.scalars().all()[:5]
                print(f"   Sample sections: {', '.join(sections)}")


async def main():
    """Main entry point."""
    print("\n" + "="*80)
    print("NEURONEXT REGULATORY INTELLIGENCE - MULTI-COUNTRY DATA INGESTION")
    print("="*80)
    print("\n[NOTE] This script now fetches REAL data from regulatory authorities.")
    print("        It no longer uses mock/simulated data.")

    # Check existing data
    await check_existing_data()

    # Add regulatory authorities
    print("\n" + "-"*80)
    print("Adding regulatory authorities...")
    print("-"*80)
    await add_regulatory_authorities()

    # Ingest data
    print("\n")
    await ingest_from_regulatory_authorities(skip_existing=True)

    # Show coverage
    await show_coverage()

    print("\n" + "="*80)
    print("[OK] Multi-country data ingestion complete!")
    print("="*80)
    print("\n[Tips]")
    print("  - Run this script again to update existing data")
    print("  - Set skip_existing=False to re-import all drugs")
    print("  - View the web interface at http://localhost:8000")
    print()


if __name__ == "__main__":
    asyncio.run(main())
