"""
Ingest EU EMA Data from Downloaded EPAR PDFs

Extracts Product Information from EPAR PDFs and stores in database.
"""

import asyncio
import sqlite3
import json
import re
from pathlib import Path
from typing import Dict, List
import uuid

# Try to import PDF extraction libraries
try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False
    print("WARNING: PyMuPDF not installed. Install with: pip install PyMuPDF")

# Database path
DB_PATH = "data/drug_ra.db"

# Downloaded EPAR PDFs
EMA_PARSED_DRUGS = {
    "Genvoya": {
        "pdf": "data/epar_genvoya.pdf",
        "epar_url": "https://www.ema.europa.eu/en/medicines/human/EPAR/genvoya",
        "product_info_url": "https://www.ema.europa.eu/en/documents/product-information/genvoya-epar-product-information_en.pdf"
    },
    "Biktarvy": {
        "pdf": "data/epar_biktarvy.pdf",
        "epar_url": "https://www.ema.europa.eu/en/medicines/human/EPAR/biktarvy",
        "product_info_url": "https://www.ema.europa.eu/en/documents/product-information/biktarvy-epar-product-information_en.pdf"
    },
    "Descovy": {
        "pdf": "data/epar_descovy.pdf",
        "epar_url": "https://www.ema.europa.eu/en/medicines/human/EPAR/descovy",
        "product_info_url": "https://www.ema.europa.eu/en/documents/product-information/descovy-epar-product-information_en.pdf"
    },
    "Epclusa": {
        "pdf": "data/epar_epclusa.pdf",
        "epar_url": "https://www.ema.europa.eu/en/medicines/human/EPAR/epclusa",
        "product_info_url": "https://www.ema.europa.eu/en/documents/product-information/epclusa-epar-product-information_en.pdf"
    },
    "Veklury": {
        "pdf": "data/epar_veklury.pdf",
        "epar_url": "https://www.ema.europa.eu/en/medicines/human/EPAR/veklury",
        "product_info_url": "https://www.ema.europa.eu/en/documents/product-information/veklury-epar-product-information_en.pdf"
    },
    "Sovaldi": {
        "pdf": "data/epar_sovaldi.pdf",
        "epar_url": "https://www.ema.europa.eu/en/medicines/human/EPAR/sovaldi",
        "product_info_url": "https://www.ema.europa.eu/en/documents/product-information/sovaldi-epar-product-information_en.pdf"
    },
    "Harvoni": {
        "pdf": "data/epar_harvoni.pdf",
        "epar_url": "https://www.ema.europa.eu/en/medicines/human/EPAR/harvoni",
        "product_info_url": "https://www.ema.europa.eu/en/documents/product-information/harvoni-epar-product-information_en.pdf"
    },
}


def extract_sections_from_pdf(pdf_path: str, drug_name: str) -> Dict[str, str]:
    """Extract sections from EPAR PDF."""
    if not HAS_PYMUPDF:
        print(f"      [ERROR] PyMuPDF not available")
        return {}

    try:
        doc = fitz.open(pdf_path)
        full_text = ""

        for page in doc:
            full_text += page.get_text()

        doc.close()

        # Parse sections based on common EPAR/Product Information patterns
        sections = {}

        # Common section headings in EU Product Information
        section_patterns = {
            r'2\.?\s*Qualitative and quantitative composition': 'Qualitative and Quantitative Composition',
            r'3\.?\s*Pharmaceutical form': 'Pharmaceutical Form',
            r'4\.?\s*Clinical particulars': 'Clinical Particulars',
            r'4\.?\s*[1-9]\.?\s*Therapeutic indications': 'Therapeutic Indications',
            r'4\.?\s*[2-9]\.?\s*Posology and method of administration': 'Posology and Method of Administration',
            r'4\.?\s*[3-9]\.?\s*Contraindications': 'Contraindications',
            r'4\.?\s*[4-9]\.?\s*Special warnings and precautions for use': 'Special Warnings and Precautions',
            r'4\.?\s*[5-9]\.?\s*Undesirable effects': 'Undesirable Effects',
            r'4\.?\s*[6-9]\.?\s*Interaction with other medicinal products': 'Interaction with Other Medicinal Products',
            r'4\.?\s*[7-9]\.?\s*Fertility, pregnancy and lactation': 'Fertility, Pregnancy and Lactation',
            r'4\.?\s*[8-9]\.?\s*Effects on ability to drive and use machines': 'Effects on Ability to Drive and Use Machines',
            r'5\.?\s*Pharmacological properties': 'Pharmacological Properties',
            r'6\.?\s*Pharmaceutical particulars': 'Pharmaceutical Particulars',
        }

        # Extract sections using regex
        for pattern, section_name in section_patterns.items():
            matches = re.finditer(pattern, full_text, re.IGNORECASE | re.MULTILINE)

            for match in matches:
                start_pos = match.end()

                # Find the next section heading
                next_section_pattern = r'\n\s*\d\.?\s*[A-Z][a-z]+'
                next_match = re.search(next_section_pattern, full_text[start_pos:], re.MULTILINE)

                if next_match:
                    end_pos = start_pos + next_match.start()
                else:
                    end_pos = min(start_pos + 3000, len(full_text))  # Limit section size

                # Extract and clean the content
                section_text = full_text[start_pos:end_pos].strip()
                section_text = re.sub(r'\n+', ' ', section_text)  # Replace newlines with spaces
                section_text = ' '.join(section_text.split())  # Normalize whitespace

                if len(section_text) > 50:  # Only add if there's meaningful content
                    sections[section_name] = section_text[:2000]  # Limit size
                    break  # Take first match

        # If no structured sections found, try simpler extraction
        if not sections:
            sections = _fallback_section_extraction(full_text)

        return sections

    except Exception as e:
        print(f"      [ERROR] Failed to extract from PDF: {e}")
        return {}


def _fallback_section_extraction(full_text: str) -> Dict[str, str]:
    """Fallback section extraction using keyword search."""
    sections = {}

    # Search for key terms and extract surrounding text
    keywords = [
        ('Therapeutic Indications', 'indication'),
        ('Posology', 'dosage'),
        ('Contraindications', 'contraindication'),
        ('Warnings', 'warning'),
        ('Adverse Reactions', 'adverse'),
        ('Pregnancy', 'pregnancy'),
    ]

    for section_name, keyword in keywords:
        # Find keyword occurrences
        pattern = section_name + r'.*?(?=\n\n|\n[A-Z]{5,})'
        match = re.search(pattern, full_text, re.IGNORECASE | re.DOTALL)

        if match:
            content = match.group(0)
            content = ' '.join(content.split())[:1500]
            if len(content) > 50:
                sections[section_name] = content

    return sections


async def get_drug_id_from_db(brand_name: str) -> str:
    """Get drug ID from database by brand name."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM drugs WHERE brand_name = ? OR generic_name = ?",
        (brand_name, brand_name)
    )
    result = cursor.fetchone()
    conn.close()

    return result[0] if result else None


async def get_authority_id(country_code: str) -> str:
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


async def create_eu_authority():
    """Create EU regulatory authority if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check if EU authority exists
    cursor.execute(
        "SELECT id FROM regulatory_authorities WHERE country_code = 'EU'"
    )
    result = cursor.fetchone()

    if not result:
        # Create EU authority
        import uuid
        authority_id = str(uuid.uuid4())

        cursor.execute("""
            INSERT INTO regulatory_authorities (
                id, country_code, country_name, authority_name,
                data_source_type, api_endpoint, is_active
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            authority_id,
            'EU',
            'European Union',
            'European Medicines Agency',
            'SCRAPER',
            'https://www.ema.europa.eu/',
            True
        ))

        conn.commit()
        print("[*] Created EU regulatory authority")
        conn.close()
        return authority_id

    conn.close()
    return result[0]


async def save_label_to_db(
    drug_id: str,
    authority_id: str,
    sections: Dict[str, str],
    source_url: str,
    drug_name: str
):
    """Save EMA label and sections to database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Create label entry
        label_id = f"ema_{drug_name.lower()}"

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
            "EPAR Product Information",
            json.dumps(sections, ensure_ascii=False),
            json.dumps({
                "source": "EMA (EU)",
                "source_type": "SCRAPER",
                "url": source_url,
                "epar_url": source_url
            })
        ))

        # Insert sections
        section_order = 0
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


async def ingest_ema_data():
    """Ingest EMA data from downloaded PDFs."""
    print("=" * 80)
    print("EU EMA DATA INGESTION")
    print("=" * 80)

    if not HAS_PYMUPDF:
        print("\n[ERROR] PyMuPDF not installed!")
        print("Install with: pip install PyMuPDF")
        return

    # Create EU authority
    authority_id = await create_eu_authority()

    print(f"\n[*] Processing {len(EMA_PARSED_DRUGS)} drugs...")

    for drug_name, info in EMA_PARSED_DRUGS.items():
        pdf_path = info['pdf']

        print(f"\n[*] {drug_name}")
        print(f"    PDF: {pdf_path}")

        # Check if PDF exists
        if not Path(pdf_path).exists():
            print(f"    [SKIP] PDF not found")
            continue

        # Get drug ID
        drug_id = await get_drug_id_from_db(drug_name)
        if not drug_id:
            print(f"    [SKIP] Drug not found in database")
            continue

        # Extract sections from PDF
        print(f"    [-] Extracting sections from PDF...")
        sections = extract_sections_from_pdf(pdf_path, drug_name)

        if sections:
            print(f"    [OK] Extracted {len(sections)} sections")

            # Save to database
            await save_label_to_db(
                drug_id,
                authority_id,
                sections,
                info['epar_url'],
                drug_name
            )
        else:
            print(f"    [WARN] No sections extracted")

    # Show summary
    print("\n" + "=" * 80)
    print("INGESTION COMPLETE")
    print("=" * 80)

    # Database state
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
    asyncio.run(ingest_ema_data())
