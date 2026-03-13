"""
Ingest UK EMC Data for Known Drugs
Uses known product IDs to fetch real UK drug label data
"""

import asyncio
import aiohttp
from bs4 import BeautifulSoup
import sqlite3
import json
import ssl
from typing import Dict, List, Optional
from pathlib import Path

# Database path
DB_PATH = "data/drug_ra.db"

# SSL context
SSL_CONTEXT = ssl.create_default_context()
SSL_CONTEXT.check_hostname = False
SSL_CONTEXT.verify_mode = ssl.CERT_NONE

# Complete mapping of all 22 drugs to known EMC product IDs
EMC_PRODUCTS = {
    # Successfully found drugs
    "Biktarvy": {
        "product_ids": ["9313", "15334"],
        "status": "verified"
    },
    "COMETRIQ": {
        "product_ids": ["4407", "4408"],
        "status": "verified"
    },
    "DESCOVY": {
        "product_ids": ["2107", "2108"],
        "status": "verified"
    },
    "Emtriva": {
        "product_ids": ["18", "3888"],
        "status": "verified"
    },
    "Epclusa": {
        "product_ids": ["11956", "14403", "14404"],
        "status": "verified"
    },
    "Genvoya": {
        "product_ids": ["6491", "6492"],
        "status": "verified"
    },
    "Sovaldi": {
        "product_ids": ["5247", "13687", "13688"],
        "status": "verified"
    },
    "Viread": {
        "product_ids": ["2895", "2910", "2911"],
        "status": "verified"
    },
    # Known URLs (from error messages)
    "Stribild": {
        "product_ids": ["3154"],
        "status": "known"
    },
    "TRODELVY": {
        "product_ids": ["12880"],
        "status": "known"
    },
    "Truvada": {
        "product_ids": ["3890"],
        "status": "known"
    },
    "Tybost": {
        "product_ids": ["1277"],
        "status": "known"
    },
    "VEMLIDY": {
        "product_ids": ["2314"],
        "status": "known"
    },
    "Veklury": {
        "product_ids": ["11597"],
        "status": "known"
    },
    "Vosevi": {
        "product_ids": ["772"],
        "status": "known"
    },
    "TECARTUS": {
        "product_ids": ["11987"],
        "status": "known"
    },
    "YESCARTA": {
        "product_ids": ["9439"],
        "status": "known"
    },
    # Additional drugs found during search
    "Cayston": {
        "product_ids": ["4456"],
        "status": "known"
    },
    "Livdelzi": {
        "product_ids": ["100486"],
        "status": "known"
    },
    # Unknown - need alternative names
    "COMPLERA": {
        "product_ids": [],
        "status": "unknown",
        "note": "May be called 'Eviplera' in UK"
    },
    "Letairis": {
        "product_ids": [],
        "status": "unknown",
        "note": "May be called 'Volibris' in UK"
    },
    "Yeztugo": {
        "product_ids": [],
        "status": "unknown",
        "note": "May be called 'Sunlenca' in UK"
    },
}


class EMCLabelScraper:
    """Scrape structured label data from EMC SmPC pages."""

    def __init__(self):
        self.base_url = "https://www.medicines.org.uk/emc"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html',
            'Accept-Language': 'en-GB,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
        }

    async def get_smpc_sections(self, product_id: str) -> Dict[str, str]:
        """Extract all sections from an SmPC document."""
        url = f"{self.base_url}/product/{product_id}/smpc"

        try:
            connector = aiohttp.TCPConnector(ssl=SSL_CONTEXT)
            async with aiohttp.ClientSession(headers=self.headers, connector=connector) as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status != 200:
                        return {}
                    html = await response.text()

            soup = BeautifulSoup(html, 'html.parser')
            sections = {}

            # EMC uses <details> and <summary> tags with sectionWrapper divs
            for details in soup.find_all('details'):
                summary = details.find('summary')
                if not summary:
                    continue

                section_name = summary.get_text(strip=True)

                # Skip if no meaningful name
                if len(section_name) < 3:
                    continue

                # Get content from sectionWrapper div
                section_wrapper = details.find('div', class_='sectionWrapper')
                if section_wrapper:
                    # Get all text content
                    content_text = section_wrapper.get_text(separator=' ', strip=True)
                    # Limit to reasonable length
                    content_text = content_text[:2000]

                    if content_text:
                        sections[section_name] = content_text

            return sections

        except Exception as e:
            print(f"      [ERROR] {e}")
            return {}

    async def get_pil_sections(self, product_id: str) -> Dict[str, str]:
        """Extract sections from a PIL document."""
        url = f"{self.base_url}/product/{product_id}/pil"

        try:
            connector = aiohttp.TCPConnector(ssl=SSL_CONTEXT)
            async with aiohttp.ClientSession(headers=self.headers, connector=connector) as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status != 200:
                        return {}
                    html = await response.text()

            soup = BeautifulSoup(html, 'html.parser')
            sections = {}

            # PIL sections are less structured - extract all headings
            for heading in soup.find_all(['h2', 'h3', 'h4']):
                text = heading.get_text(strip=True)

                # Get content after heading
                content = []
                current = heading.find_next_sibling()
                while current and current.name not in ['h2', 'h3', 'h4']:
                    text_content = current.get_text(strip=True)
                    if text_content:
                        content.append(text_content)
                    current = current.find_next_sibling()

                if content:
                    sections[text] = ' '.join(content)[:1000]

            return sections

        except Exception as e:
            return {}


async def get_drug_id_from_db(brand_name: str) -> Optional[str]:
    """Get drug ID from database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM drugs WHERE brand_name = ? OR generic_name = ?",
        (brand_name, brand_name)
    )
    result = cursor.fetchone()
    conn.close()

    return result[0] if result else None


async def get_authority_id(country_code: str) -> Optional[str]:
    """Get regulatory authority ID from database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM regulatory_authorities WHERE country_code = ?",
        (country_code,)
    )
    result = cursor.fetchone()
    conn.close()

    return result[0] if result else None


async def save_label_to_db(
    drug_id: str,
    authority_id: str,
    sections: Dict[str, str],
    source_url: str,
    product_id: str
):
    """Save label and sections to database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Create label entry
        label_id = f"emc_{product_id}"

        # Check if label exists
        cursor.execute(
            "SELECT id FROM drug_labels WHERE id = ?",
            (label_id,)
        )
        existing = cursor.fetchone()

        if existing:
            print(f"      [SKIP] Label already exists")
            conn.close()
            return

        # Insert label
        cursor.execute("""
            INSERT INTO drug_labels (id, drug_id, authority_id, label_type,
                                     effective_date, raw_content, meta, version)
            VALUES (?, ?, ?, ?, date('now'), ?, ?, 1)
        """, (
            label_id,
            drug_id,
            authority_id,
            "SmPC",
            json.dumps(sections, ensure_ascii=False),
            json.dumps({
                "source": "EMC (UK)",
                "source_type": "SCRAPER",
                "url": source_url,
                "product_id": product_id
            })
        ))

        # Insert sections
        section_order = 0
        import uuid
        for section_name, content in sections.items():
            section_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO label_sections (id, label_id, section_name, section_order, content)
                VALUES (?, ?, ?, ?, ?)
            """, (section_id, label_id, section_name, section_order, content))
            section_order += 1

        conn.commit()
        print(f"      [SAVED] {len(sections)} sections")

    except Exception as e:
        print(f"      [ERROR] Failed to save: {e}")
        conn.rollback()
    finally:
        conn.close()


async def ingest_uk_data_for_drug(brand_name: str, product_ids: List[str], scraper: EMCLabelScraper):
    """Ingest UK EMC data for a single drug."""
    print(f"\n[*] {brand_name}")

    # Get drug ID
    drug_id = await get_drug_id_from_db(brand_name)
    if not drug_id:
        print(f"    [SKIP] Drug not found in database")
        return

    # Get UK authority ID
    authority_id = await get_authority_id("GB")
    if not authority_id:
        print(f"    [SKIP] GB authority not found")
        return

    # Fetch data for each product ID
    for product_id in product_ids:
        print(f"    [-] Product ID: {product_id}")

        # Get SmPC sections
        smpc_sections = await scraper.get_smpc_sections(product_id)
        if smpc_sections:
            print(f"      [OK] SmPC: {len(smpc_sections)} sections")
            source_url = f"https://www.medicines.org.uk/emc/product/{product_id}/smpc"
            await save_label_to_db(drug_id, authority_id, smpc_sections, source_url, product_id)
        else:
            print(f"      [WARN] No SmPC sections found")

        # Be respectful
        await asyncio.sleep(1)


async def main():
    """Main ingestion function."""
    print("=" * 80)
    print("UK EMC DATA INGESTION")
    print("=" * 80)
    print(f"Ingesting data for {len(EMC_PRODUCTS)} drugs...")
    print("=" * 80)

    scraper = EMCLabelScraper()

    for brand_name, data in EMC_PRODUCTS.items():
        if not data["product_ids"]:
            print(f"\n[?] {brand_name}")
            print(f"    [INFO] {data.get('note', 'No product IDs known')}")
            continue

        await ingest_uk_data_for_drug(brand_name, data["product_ids"], scraper)

    print("\n" + "=" * 80)
    print("INGESTION COMPLETE")
    print("=" * 80)

    # Show summary
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ra.country_code, COUNT(dl.id) as count
        FROM drug_labels dl
        JOIN regulatory_authorities ra ON dl.authority_id = ra.id
        GROUP BY ra.country_code
        ORDER BY ra.country_code
    """)

    print("\nDatabase state:")
    for row in cursor.fetchall():
        country, count = row
        print(f"  {country}: {count} labels")
    conn.close()


if __name__ == "__main__":
    asyncio.run(main())
