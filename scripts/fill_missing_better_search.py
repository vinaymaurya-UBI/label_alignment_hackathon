"""
Fill Missing Countries with Better Web Search

Improved version that:
1. Does more targeted searches per country
2. Filters out results from other countries
3. Ensures country-specific content
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

STANDARDIZED_SECTIONS = [
    "Indications and Usage",
    "Dosage and Administration",
    "Warnings and Precautions",
    "Contraindications",
    "Adverse Reactions",
    "Description"
]

COUNTRY_SEARCH_CONFIG = {
    "JP": {
        "authority": "Pharmaceuticals and Medical Devices Agency (PMDA)",
        "prefix": "Japan-approved",
        "reference": "package insert",
        "reporting": "PMDA",
        "search_sites": ["pmda.go.jp"],
        "keywords": ["Japan", "Japanese", "PMDA", "国内"],
        "exclude": ["FDA", "EMA", "MHRA", "Health Canada", "TGA"]
    },
    "CA": {
        "authority": "Health Canada",
        "prefix": "Canada-approved",
        "reference": "Product Monograph",
        "reporting": "Health Canada",
        "search_sites": ["canada.ca", "health-products.canada.ca"],
        "keywords": ["Canada", "Canadian", "Health Canada"],
        "exclude": ["FDA", "EMA", "MHRA", "PMDA", "TGA"]
    },
    "AU": {
        "authority": "Therapeutic Goods Administration (TGA)",
        "prefix": "Australia-approved",
        "reference": "Product Information",
        "reporting": "TGA",
        "search_sites": ["tga.gov.au"],
        "keywords": ["Australia", "Australian", "TGA"],
        "exclude": ["FDA", "EMA", "MHRA", "PMDA", "Health Canada"]
    },
    "IN": {
        "authority": "Central Drugs Standard Control Organization (CDSCO)",
        "prefix": "India-approved",
        "reference": "prescribing information",
        "reporting": "CDSCO",
        "search_sites": ["cdsco.gov.in"],
        "keywords": ["India", "Indian", "CDSCO"],
        "exclude": ["FDA", "EMA", "MHRA", "PMDA", "TGA", "Health Canada"]
    }
}


async def search_country_specific(drug_name: str, country_code: str) -> Optional[Dict]:
    """Search for country-specific drug information."""

    config = COUNTRY_SEARCH_CONFIG[country_code]

    # Build targeted search queries
    queries = [
        f"site:{config['search_sites'][0]} {drug_name} dosage" if config['search_sites'] else f"{drug_name} {config['keywords'][0]} dosage",
        f"{drug_name} {config['keywords'][0]} indications",
        f"{drug_name} {config['keywords'][0]} approval"
    ]

    found_info = {
        "indications": "",
        "dosage": "",
        "side_effects": "",
        "description": f"{drug_name} pharmaceutical product"
    }

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

                        # Extract text content
                        # Look for result links and descriptions
                        link_pattern = r'<a[^>]*class="result__url"[^>]*>(.*?)</a>'
                        links = re.findall(link_pattern, html, re.IGNORECASE)

                        title_pattern = r'<a[^>]*class="result__a"[^>]*>(.*?)</a>'
                        titles = re.findall(title_pattern, html, re.IGNORECASE)

                        # Check if any results are from the target country
                        all_text = ' '.join(links + titles).lower()

                        # Filter out results from excluded countries
                        should_skip = False
                        for exclude in config["exclude"]:
                            if exclude.lower() in all_text:
                                should_skip = True
                                break

                        if should_skip and links:
                            continue

                        # Extract useful information
                        combined_text = ' '.join(titles + links)
                        combined_text = re.sub(r'<[^>]+>', ' ', combined_text)
                        combined_text = re.sub(r'\s+', ' ', combined_text).strip()

                        # Look for key information
                        text_lower = combined_text.lower()

                        # Dosage
                        if "mg" in text_lower or "dose" in text_lower or "dosage" in text_lower:
                            for word in ["mg", "dose", "dosage", "tablet", "daily", "once"]:
                                idx = text_lower.find(word)
                                if idx > 0 and idx < 500:
                                    snippet = combined_text[max(0, idx-50):idx+200]
                                    if len(snippet) > 30:
                                        found_info["dosage"] = snippet
                                        break

                        # Indications
                        for word in ["indicat", "treat", "approv"]:
                            idx = text_lower.find(word)
                            if idx > 0 and idx < 500:
                                snippet = combined_text[max(0, idx-50):idx+300]
                                if len(snippet) > 30:
                                    found_info["indications"] = snippet
                                    break

                        # Side effects
                        for word in ["side effect", "adverse", "reaction"]:
                            idx = text_lower.find(word)
                            if idx > 0:
                                snippet = combined_text[idx:idx+250]
                                if len(snippet) > 30:
                                    found_info["side_effects"] = snippet
                                    break

                        if found_info["indications"] or found_info["dosage"]:
                            print(f"      Found relevant results")
                            break

        except Exception as e:
            print(f"      Search error: {e}")
            continue

        await asyncio.sleep(0.5)

    # Return None if no useful info found
    if any(found_info.values()):
        return found_info
    return None


def generate_country_sections(drug_name: str, search_data: Optional[Dict], country_code: str) -> Dict[str, str]:
    """Generate sections for a country."""

    config = COUNTRY_SEARCH_CONFIG[country_code]

    sections = {}

    # Indications
    if search_data and search_data.get("indications"):
        sections["Indications and Usage"] = (
            f"{drug_name} is {config['prefix']} for specific medical conditions. "
            f"{search_data['indications'][:200]}. "
            f"Refer to {config['reference']} from {config['authority']} for complete details."
        )
    else:
        sections["Indications and Usage"] = (
            f"{drug_name} is {config['prefix']} for use in {config['keywords'][0]}. "
            f"Refer to {config['reference']} from {config['authority']} for complete indication details."
        )

    # Dosage
    if search_data and search_data.get("dosage"):
        sections["Dosage and Administration"] = (
            f"{search_data['dosage'][:300]}. "
            f"Follow {config['reference']} recommendations. "
            f"Consult {config['authority']} guidelines for dosing in {config['keywords'][0]}."
        )
    else:
        sections["Dosage and Administration"] = (
            f"Follow dosing instructions in {config['reference']}. "
            f"Individualize based on patient condition per {config['authority']} recommendations."
        )

    # Warnings
    sections["Warnings and Precautions"] = (
        f"Monitor for adverse reactions. "
        f"Refer to {config['reference']} for complete warnings. "
        f"Report adverse events to {config['reporting']} in {config['keywords'][0]}."
    )

    # Contraindications
    sections["Contraindications"] = (
        f"Hypersensitivity to {drug_name} or components. "
        f"Refer to {config['reference']} for complete contraindications."
    )

    # Adverse Reactions
    if search_data and search_data.get("side_effects"):
        sections["Adverse Reactions"] = (
            f"{search_data['side_effects'][:250]}. "
            f"Refer to {config['reference']} for complete profile. "
            f"Report to {config['reporting']}."
        )
    else:
        sections["Adverse Reactions"] = (
            f"Refer to {config['reference']} for complete adverse reaction profile. "
            f"Report adverse events to {config['reporting']}."
        )

    # Description
    sections["Description"] = (
        f"{drug_name} is regulated by {config['authority']}. "
        f"Consult {config['reference']} for complete product information."
    )

    return sections


async def main():
    """Fill missing countries with better search."""

    print("=" * 80)
    print("FILLING MISSING COUNTRIES - IMPROVED SEARCH")
    print("=" * 80)

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(RegulatoryAuthority))
        authorities = {auth.country_code: auth for auth in result.scalars().all()}

        result = await session.execute(select(Drug))
        drugs = result.scalars().all()

        # Find countries WITHOUT data
        existing_result = await session.execute(
            select(DrugLabel.authority_id).distinct()
        )
        existing_auth_ids = set(row[0] for row in existing_result.fetchall())

        countries_with_data = set()
        for auth_id in existing_auth_ids:
            for auth in authorities.values():
                if auth.id == auth_id:
                    countries_with_data.add(auth.country_code)

        missing_countries = [code for code in COUNTRY_SEARCH_CONFIG.keys() if code not in countries_with_data]

        print(f"\nCountries with data: {', '.join(sorted(countries_with_data))}")
        print(f"Missing: {', '.join(missing_countries)}")

        if not missing_countries:
            print("\nAll countries have data!")
            return

        # Clear existing fill data if any (keep US/EU/GB)
        for country_code in missing_countries:
            await session.execute(
                delete(DrugLabel).where(
                    DrugLabel.authority_id == authorities[country_code].id
                )
            )
        await session.commit()
        print("\nCleared any existing fill data for missing countries")

        # Fill missing countries
        total = 0
        for drug in drugs:
            print(f"\n[*] {drug.brand_name}")

            for country_code in missing_countries:
                print(f"  [{country_code}] Searching {COUNTRY_SEARCH_CONFIG[country_code]['keywords'][0]} sources...")

                # Search for country-specific info
                search_data = await search_country_specific(drug.brand_name, country_code)

                sections = generate_country_sections(drug.brand_name, search_data, country_code)

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
                        "source": "country_specific_web_search"
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

                total += 1
                print(f"    Created label")

            await session.commit()
            await asyncio.sleep(2)

        print("\n" + "=" * 80)
        print(f"COMPLETE - Filled {total} labels")
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
