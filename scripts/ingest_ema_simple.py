"""
Simplified EMA Data Ingestion - Store full EPAR text
"""

import asyncio
import sqlite3
import json
import fitz  # PyMuPDF
from pathlib import Path
from typing import Dict
import uuid

DB_PATH = "data/drug_ra.db"

EMA_DRUGS = {
    "Genvoya": {"pdf": "data/epar_genvoya.pdf"},
    "Biktarvy": {"pdf": "data/epar_biktarvy.pdf"},
    "Descovy": {"pdf": "data/epar_descovy.pdf"},
    "Epclusa": {"pdf": "data/epar_epclusa.pdf"},
    "Veklury": {"pdf": "data/epar_veklury.pdf"},
    "Sovaldi": {"pdf": "data/epar_sovaldi.pdf"},
    "Harvoni": {"pdf": "data/epar_harvoni.pdf"},
}


async def get_drug_id(brand_name: str) -> str:
    """Get drug ID from database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM drugs WHERE brand_name = ? OR generic_name = ?", (brand_name, brand_name))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None


async def create_eu_authority():
    """Create EU authority if needed."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM regulatory_authorities WHERE country_code = 'EU'")
    result = cursor.fetchone()

    if not result:
        authority_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO regulatory_authorities (id, country_code, country_name, authority_name, data_source_type, is_active)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (authority_id, 'EU', 'European Union', 'European Medicines Agency', 'SCRAPER', True))
        conn.commit()
        print("[*] Created EU regulatory authority")
        conn.close()
        return authority_id

    conn.close()
    return result[0]


async def ingest_ema_simple():
    """Ingest EMA data with simple full-text extraction."""
    print("=" * 80)
    print("EU EMA DATA INGESTION (Simplified)")
    print("=" * 80)

    authority_id = await create_eu_authority()

    ingested = 0

    for drug_name, info in EMA_DRUGS.items():
        pdf_path = info['pdf']

        print(f"\n[*] {drug_name}")

        if not Path(pdf_path).exists():
            print(f"    [SKIP] PDF not found")
            continue

        drug_id = await get_drug_id(drug_name)
        if not drug_id:
            print(f"    [SKIP] Drug not in database")
            continue

        # Extract all text from PDF
        try:
            doc = fitz.open(pdf_path)
            full_text = ""

            for page in doc:
                full_text += page.get_text()

            doc.close()

            # Create simple sections based on content
            sections = {
                "EPAR Product Information (Full Text)": full_text[:5000]  # First 5000 chars
            }

            # Save to database
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            label_id = f"ema_{drug_name.lower()}"

            cursor.execute("""
                INSERT INTO drug_labels (id, drug_id, authority_id, label_type, effective_date, raw_content, meta, version)
                VALUES (?, ?, ?, ?, date('now'), ?, ?, 1)
            """, (
                label_id,
                drug_id,
                authority_id,
                "EPAR",
                json.dumps(sections, ensure_ascii=False),
                json.dumps({
                    "source": "EMA (EU)",
                    "source_type": "SCRAPER",
                    "url": f"https://www.ema.europa.eu/en/medicines/human/EPAR/{drug_name.lower()}"
                })
            ))

            # Add section
            section_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO label_sections (id, label_id, section_name, section_order, content)
                VALUES (?, ?, ?, ?, ?)
            """, (section_id, label_id, "EPAR Product Information", 0, sections["EPAR Product Information (Full Text)"]))

            conn.commit()
            conn.close()

            print(f"    [SAVED] EPAR data ({len(full_text)} chars)")
            ingested += 1

        except Exception as e:
            print(f"    [ERROR] {e}")

    print("\n" + "=" * 80)
    print(f"INGESTION COMPLETE: {ingested} drugs")
    print("=" * 80)

    # Show database state
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ra.country_code, COUNT(dl.id) as label_count
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
    asyncio.run(ingest_ema_simple())
