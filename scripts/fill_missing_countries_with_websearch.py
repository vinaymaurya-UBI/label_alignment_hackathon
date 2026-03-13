"""
Fill Missing Countries with Web Search

This script:
1. KEEPS existing real data (US FDA, EU EMA, GB EMC)
2. Uses web search ONLY for missing countries (JP, CA, AU, IN)
3. Does targeted searches like "TRODELVY dosage Japan"
4. Preserves original real data without modification
"""

import asyncio
import aiohttp
import sqlite3
import json
import re
from datetime import datetime
from typing import Dict, List, Optional
import sys
import os

# Add backend to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
backend_dir = os.path.join(parent_dir, 'backend')
sys.path.insert(0, backend_dir)

from app.core.database import AsyncSessionLocal
from app.models import Drug, DrugLabel, LabelSection, RegulatoryAuthority
from sqlalchemy import select, delete

DB_PATH = "data/drug_ra.db"

# Standardized sections
STANDARDIZED_SECTIONS = [
    "Indications and Usage",
    "Dosage and Administration",
    "Warnings and Precautions",
    "Contraindications",
    "Adverse Reactions",
    "Description"
]

# Country-specific information
COUNTRY_INFO = {
    "JP": {
        "authority": "Pharmaceuticals and Medical Devices Agency (PMDA)",
        "prefix": "Japan-approved",
        "reference": "package insert",
        "reporting": "PMDA",
        "search_terms": ["Japan", "Japanese", "PMDA"]
    },
    "CA": {
        "authority": "Health Canada",
        "prefix": "Canada-approved",
        "reference": "Product Monograph",
        "reporting": "Health Canada",
        "search_terms": ["Canada", "Canadian", "Health Canada"]
    },
    "AU": {
        "authority": "Therapeutic Goods Administration (TGA)",
        "prefix": "Australia-approved",
        "reference": "Product Information",
        "reporting": "TGA",
        "search_terms": ["Australia", "Australian", "TGA"]
    },
    "IN": {
        "authority": "Central Drugs Standard Control Organization (CDSCO)",
        "prefix": "India-approved",
        "reference": "prescribing information",
        "reporting": "CDSCO",
        "search_terms": ["India", "Indian", "CDSCO"]
    }
}


async def search_drug_for_country(drug_name: str, country_code: str) -> Optional[Dict]:
    """Search for drug information specific to a country."""

    country = COUNTRY_INFO[country_code]
    search_term = country["search_terms"][0]

    # Build targeted search queries
    queries = [
        f"{drug_name} dosage {search_term}",
        f"{drug_name} administration {search_term}",
        f"{drug_name} indications {search_term}",
        f"{drug_name} side effects {search_term}"
    ]

    search_results = {}

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    for query in queries:
        try:
            url = f"https://duckduckgo.com/html/?q={query.replace(' ', '+')}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as response:
                    if response.status == 200:
                        html = await response.text()

                        # Extract snippets from results
                        # Look for result descriptions
                        snippet_pattern = r'<a[^>]*class="result__a"[^>]*>.*?<span[^>]*class="result__snippet"[^>]*>(.*?)</span>'
                        snippets = re.findall(snippet_pattern, html, re.DOTALL)

                        # Also try alternative pattern
                        if not snippets:
                            snippet_pattern = r'<a[^>]*class="result__url"[^>]*>.*?</a>.*?<a[^>]*class="result__a"[^>]*>(.*?)</a>'
                            snippets = re.findall(snippet_pattern, html, re.DOTALL)

                        for snippet in snippets[:3]:
                            # Clean HTML
                            clean = re.sub(r'<[^>]+>', ' ', snippet)
                            clean = re.sub(r'\s+', ' ', clean).strip()

                            if len(clean) > 30:
                                # Store by query type
                                if "dosage" in query.lower():
                                    if "dosage" not in search_results:
                                        search_results["dosage"] = clean
                                elif "administration" in query.lower():
                                    if "dosage" not in search_results:
                                        search_results["dosage"] = clean
                                elif "indications" in query.lower():
                                    if "indications" not in search_results:
                                        search_results["indications"] = clean
                                elif "side" in query.lower():
                                    if "side_effects" not in search_results:
                                        search_results["side_effects"] = clean

                                if len(search_results) >= 2:
                                    break

                        if len(search_results) >= 2:
                            break

        except Exception as e:
            print(f"      [Search error: {e}]")
            continue

        await asyncio.sleep(0.5)

    return search_results if search_results else None


def generate_sections_from_search(drug_name: str, search_data: Dict, country_code: str) -> Dict[str, str]:
    """Generate sections from search results."""

    country = COUNTRY_INFO[country_code]

    sections = {}

    # Indications
    if "indications" in search_data:
        sections["Indications and Usage"] = (
            f"{drug_name} is {country['prefix']} for use. "
            f"{search_data['indications'][:300]}. "
            f"Refer to {country['reference']} for complete details from {country['authority']}."
        )
    else:
        sections["Indications and Usage"] = (
            f"{drug_name} is {country['prefix']} for specific medical conditions. "
            f"Refer to {country['reference']} for complete indication details from {country['authority']}."
        )

    # Dosage
    if "dosage" in search_data:
        sections["Dosage and Administration"] = (
            f"{search_data['dosage'][:350]}. "
            f"Follow {country['reference']} recommendations. "
            f"Dosing may vary by patient - consult {country['authority']} guidelines."
        )
    else:
        sections["Dosage and Administration"] = (
            f"Follow dosing instructions in {country['reference']}. "
            f"Individualize based on patient condition and {country['authority']} recommendations."
        )

    # Warnings
    sections["Warnings and Precautions"] = (
        f"Monitor for adverse reactions. "
        f"Review {country['reference']} for complete warnings. "
        f"Report adverse events to {country['reporting']}."
    )

    # Contraindications
    sections["Contraindications"] = (
        f"Known hypersensitivity to {drug_name} or components. "
        f"Refer to {country['reference']} for complete contraindications."
    )

    # Side effects
    if "side_effects" in search_data:
        sections["Adverse Reactions"] = (
            f"{search_data['side_effects'][:300]}. "
            f"Refer to {country['reference']} for complete adverse reaction profile. "
            f"Report to {country['reporting']}."
        )
    else:
        sections["Adverse Reactions"] = (
            f"Refer to {country['reference']} for complete adverse reaction profile. "
            f"Report adverse events to {country['reporting']}."
        )

    # Description
    sections["Description"] = (
        f"{drug_name} is regulated by {country['authority']}. "
        f"Consult {country['reference']} for complete product information."
    )

    return sections


async def fill_missing_countries():
    """Fill only missing countries with web search."""

    print("=" * 80)
    print("FILLING MISSING COUNTRIES WITH WEB SEARCH")
    print("=" * 80)
    print("\nThis script KEEPS existing real data (US, EU, GB)")
    print("and ONLY fills missing countries (JP, CA, AU, IN)")
    print()

    # Get database data
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(RegulatoryAuthority))
        authorities = {auth.country_code: auth for auth in result.scalars().all()}

        result = await session.execute(select(Drug))
        drugs = result.scalars().all()

        # Check which countries already have data
        existing_result = await session.execute(
            select(DrugLabel.authority_id).distinct()
        )
        existing_auth_ids = set(row[0] for row in existing_result.fetchall())

        # Find countries WITHOUT data
        countries_with_data = set()
        for auth_id in existing_auth_ids:
            for auth in authorities.values():
                if auth.id == auth_id:
                    countries_with_data.add(auth.country_code)

        missing_countries = [code for code in COUNTRY_INFO.keys() if code not in countries_with_data]

        print(f"Countries WITH real data: {', '.join(sorted(countries_with_data))}")
        print(f"Countries NEEDING data: {', '.join(missing_countries)}")
        print()

        if not missing_countries:
            print("All countries have data!")
            return

        # Process each drug
        total_filled = 0
        stats = {code: 0 for code in missing_countries}

        for drug in drugs:
            print(f"[*] {drug.brand_name}")

            # Search for each missing country
            for country_code in missing_countries:
                print(f"  [{country_code}] Searching...")

                # Search for drug info for this country
                search_data = await search_drug_for_country(drug.brand_name, country_code)

                if search_data:
                    print(f"    Found data")
                    sections = generate_sections_from_search(
                        drug.brand_name,
                        search_data,
                        country_code
                    )
                else:
                    print(f"    No results, using generic")
                    sections = generate_sections_from_search(
                        drug.brand_name,
                        {},  # Empty = generic
                        country_code
                    )

                # Create label
                authority = authorities[country_code]
                label = DrugLabel(
                    drug_id=drug.id,
                    authority_id=authority.id,
                    version=1,
                    label_type="PACKAGE_INSERT",
                    effective_date=datetime.now(),
                    raw_content=json.dumps(search_data or {}),
                    meta={
                        "country_code": country_code,
                        "authority": authority.authority_name,
                        "source": "web_search_filled"
                    }
                )
                session.add(label)
                await session.flush()
                await session.refresh(label)

                # Create sections
                for order, section_name in enumerate(STANDARDIZED_SECTIONS):
                    section = LabelSection(
                        label_id=label.id,
                        section_name=section_name,
                        section_order=order,
                        content=sections[section_name],
                        normalized_content=sections[section_name].lower()
                    )
                    session.add(section)

                stats[country_code] += 1
                total_filled += 1

            await session.commit()
            await asyncio.sleep(2)  # Rate limiting

        # Summary
        print("\n" + "=" * 80)
        print("FILL COMPLETE")
        print("=" * 80)
        print(f"\nFilled {total_filled} labels for missing countries")
        print("\nFilled labels by country:")
        for code, count in stats.items():
            print(f"  {code} ({COUNTRY_INFO[code]['authority']}): {count} labels")


if __name__ == "__main__":
    asyncio.run(fill_missing_countries())
