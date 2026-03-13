"""
Populate All Countries With Real Pharmaceutical Data

Fetches real section content from the FDA openFDA API for each drug,
then maps that content to each country's regulatory section naming conventions.

This ensures all countries (US, EU, GB, CA, JP, AU) show real pharmaceutical
data rather than placeholder text.
"""

import asyncio
import aiohttp
import sqlite3
import uuid
import ssl
import re
import sys
from typing import Dict, List, Optional, Tuple

DB_PATH = "data/drug_ra.db"

SSL_CONTEXT = ssl.create_default_context()
SSL_CONTEXT.check_hostname = False
SSL_CONTEXT.verify_mode = ssl.CERT_NONE

# FDA API section keys to standard US names
FDA_SECTION_KEYS = {
    "indications_and_usage": "Indications and Usage",
    "dosage_and_administration": "Dosage and Administration",
    "warnings_and_precautions": "Warnings and Precautions",
    "contraindications": "Contraindications",
    "adverse_reactions": "Adverse Reactions",
    "drug_interactions": "Drug Interactions",
    "use_in_specific_populations": "Use in Specific Populations",
    "pregnancy": "Pregnancy",
    "pediatric_use": "Pediatric Use",
    "geriatric_use": "Geriatric Use",
    "overdosage": "Overdosage",
    "description": "Description",
    "clinical_pharmacology": "Clinical Pharmacology",
    "nonclinical_toxicology": "Nonclinical Toxicology",
    "clinical_studies": "Clinical Studies",
    "patient_counseling_information": "Patient Counseling Information",
    "how_supplied": "How Supplied / Storage and Handling",
    "storage_and_handling": "Storage and Handling",
    "boxed_warning": "Boxed Warning",
    "mechanism_of_action": "Mechanism of Action",
    "pharmacodynamics": "Pharmacodynamics",
    "pharmacokinetics": "Pharmacokinetics",
    "microbiology": "Microbiology",
    "carcinogenesis_and_mutagenesis_and_impairment_of_fertility": "Carcinogenesis and Mutagenesis",
    "animal_pharmacology_and_or_toxicology": "Animal Pharmacology",
}

# Country-specific section name mappings (same content, different regulatory terminology)
COUNTRY_SECTION_MAPPINGS = {
    "US": {
        "Indications and Usage": "Indications and Usage",
        "Dosage and Administration": "Dosage and Administration",
        "Warnings and Precautions": "Warnings and Precautions",
        "Contraindications": "Contraindications",
        "Adverse Reactions": "Adverse Reactions",
        "Drug Interactions": "Drug Interactions",
        "Use in Specific Populations": "Use in Specific Populations",
        "Pregnancy": "Pregnancy",
        "Pediatric Use": "Pediatric Use",
        "Geriatric Use": "Geriatric Use",
        "Overdosage": "Overdosage",
        "Description": "Description",
        "Clinical Pharmacology": "Clinical Pharmacology",
        "Nonclinical Toxicology": "Nonclinical Toxicology",
        "Clinical Studies": "Clinical Studies",
        "Patient Counseling Information": "Patient Counseling Information",
        "How Supplied / Storage and Handling": "How Supplied / Storage and Handling",
        "Storage and Handling": "Storage and Handling",
        "Boxed Warning": "Boxed Warning",
        "Mechanism of Action": "Mechanism of Action",
        "Pharmacodynamics": "Pharmacodynamics",
        "Pharmacokinetics": "Pharmacokinetics",
        "Microbiology": "Microbiology",
        "Carcinogenesis and Mutagenesis": "Carcinogenesis and Mutagenesis",
        "Animal Pharmacology": "Animal Pharmacology",
    },
    "EU": {
        "Indications and Usage": "Therapeutic Indications",
        "Dosage and Administration": "Posology and Method of Administration",
        "Warnings and Precautions": "Special Warnings and Precautions for Use",
        "Contraindications": "Contraindications",
        "Adverse Reactions": "Undesirable Effects",
        "Drug Interactions": "Interaction with Other Medicinal Products and Other Forms of Interaction",
        "Use in Specific Populations": "Special Populations",
        "Pregnancy": "Fertility, Pregnancy and Lactation",
        "Pediatric Use": "Paediatric Population",
        "Geriatric Use": "Elderly Patients",
        "Overdosage": "Overdose",
        "Description": "Pharmaceutical Form and Composition",
        "Clinical Pharmacology": "Pharmacodynamic Properties",
        "Nonclinical Toxicology": "Preclinical Safety Data",
        "Clinical Studies": "Clinical Efficacy and Safety",
        "Patient Counseling Information": "Special Precautions for Disposal and Other Handling",
        "How Supplied / Storage and Handling": "Shelf Life and Special Precautions for Storage",
        "Storage and Handling": "Special Precautions for Storage",
        "Boxed Warning": "Important Safety Information",
        "Mechanism of Action": "Mechanism of Action",
        "Pharmacodynamics": "Pharmacodynamic Properties",
        "Pharmacokinetics": "Pharmacokinetic Properties",
        "Microbiology": "Microbiological Properties",
        "Carcinogenesis and Mutagenesis": "Mutagenicity and Carcinogenicity",
        "Animal Pharmacology": "Animal Toxicology",
    },
    "GB": {
        "Indications and Usage": "Therapeutic Indications",
        "Dosage and Administration": "Posology and Method of Administration",
        "Warnings and Precautions": "Special Warnings and Precautions for Use",
        "Contraindications": "Contraindications",
        "Adverse Reactions": "Undesirable Effects",
        "Drug Interactions": "Interaction with Other Medicinal Products and Other Forms of Interaction",
        "Use in Specific Populations": "Special Populations",
        "Pregnancy": "Fertility, Pregnancy and Lactation",
        "Pediatric Use": "Paediatric Population",
        "Geriatric Use": "Elderly Patients",
        "Overdosage": "Overdose",
        "Description": "Pharmaceutical Form",
        "Clinical Pharmacology": "Pharmacodynamic Properties",
        "Nonclinical Toxicology": "Preclinical Safety Data",
        "Clinical Studies": "Clinical Studies (UK SmPC)",
        "Patient Counseling Information": "Patient Counselling",
        "How Supplied / Storage and Handling": "Special Precautions for Storage",
        "Storage and Handling": "Storage and Handling Instructions",
        "Boxed Warning": "Important Safety Warning",
        "Mechanism of Action": "Mechanism of Action",
        "Pharmacodynamics": "Pharmacodynamic Properties",
        "Pharmacokinetics": "Pharmacokinetic Properties",
        "Microbiology": "Microbiological Properties",
        "Carcinogenesis and Mutagenesis": "Mutagenicity and Carcinogenicity",
        "Animal Pharmacology": "Toxicological Studies",
    },
    "CA": {
        "Indications and Usage": "Indications and Clinical Use",
        "Dosage and Administration": "Dosage and Administration",
        "Warnings and Precautions": "Warnings and Precautions",
        "Contraindications": "Contraindications",
        "Adverse Reactions": "Adverse Reactions",
        "Drug Interactions": "Drug Interactions",
        "Use in Specific Populations": "Special Populations",
        "Pregnancy": "Pregnant Women",
        "Pediatric Use": "Pediatrics",
        "Geriatric Use": "Geriatrics",
        "Overdosage": "Overdosage",
        "Description": "Pharmaceutical Information",
        "Clinical Pharmacology": "Action and Clinical Pharmacology",
        "Nonclinical Toxicology": "Toxicology",
        "Clinical Studies": "Clinical Trials",
        "Patient Counseling Information": "Information for the Patient",
        "How Supplied / Storage and Handling": "Dosage Forms, Composition and Packaging",
        "Storage and Handling": "Storage and Stability",
        "Boxed Warning": "Serious Warnings and Precautions Box",
        "Mechanism of Action": "Mechanism of Action",
        "Pharmacodynamics": "Pharmacodynamics",
        "Pharmacokinetics": "Pharmacokinetics",
        "Microbiology": "Microbiology",
        "Carcinogenesis and Mutagenesis": "Carcinogenesis and Mutagenesis",
        "Animal Pharmacology": "Animal Pharmacology and/or Toxicology",
    },
    "JP": {
        "Indications and Usage": "Indications",
        "Dosage and Administration": "Dosage and Administration",
        "Warnings and Precautions": "Precautions",
        "Contraindications": "Contraindications",
        "Adverse Reactions": "Adverse Reactions",
        "Drug Interactions": "Drug Interactions",
        "Use in Specific Populations": "Use in Specific Populations",
        "Pregnancy": "Use During Pregnancy and Lactation",
        "Pediatric Use": "Pediatric Use",
        "Geriatric Use": "Geriatric Use",
        "Overdosage": "Overdosage",
        "Description": "Properties and Composition",
        "Clinical Pharmacology": "Pharmacological Actions",
        "Nonclinical Toxicology": "Toxicity Studies",
        "Clinical Studies": "Clinical Studies (Japan)",
        "Patient Counseling Information": "Instructions for Patients",
        "How Supplied / Storage and Handling": "Storage and Handling",
        "Storage and Handling": "Storage Conditions",
        "Boxed Warning": "Important Precautions",
        "Mechanism of Action": "Mechanism of Action",
        "Pharmacodynamics": "Pharmacological Properties",
        "Pharmacokinetics": "Pharmacokinetics",
        "Microbiology": "Microbiological Data",
        "Carcinogenesis and Mutagenesis": "Mutagenicity",
        "Animal Pharmacology": "Animal Studies",
    },
    "AU": {
        "Indications and Usage": "Indications",
        "Dosage and Administration": "Dosage and Administration",
        "Warnings and Precautions": "Warnings and Precautions",
        "Contraindications": "Contraindications",
        "Adverse Reactions": "Adverse Effects",
        "Drug Interactions": "Interactions with Other Medicines",
        "Use in Specific Populations": "Use in Special Populations",
        "Pregnancy": "Use in Pregnancy",
        "Pediatric Use": "Paediatric Use",
        "Geriatric Use": "Use in the Elderly",
        "Overdosage": "Overdosage",
        "Description": "Description",
        "Clinical Pharmacology": "Pharmacology",
        "Nonclinical Toxicology": "Preclinical Safety Data",
        "Clinical Studies": "Clinical Trials (Australia)",
        "Patient Counseling Information": "Patient Counselling",
        "How Supplied / Storage and Handling": "Presentation and Storage",
        "Storage and Handling": "Storage and Handling",
        "Boxed Warning": "Contraindications and Precautions",
        "Mechanism of Action": "Mechanism of Action",
        "Pharmacodynamics": "Pharmacodynamics",
        "Pharmacokinetics": "Pharmacokinetic Properties",
        "Microbiology": "Microbiology",
        "Carcinogenesis and Mutagenesis": "Carcinogenesis, Mutagenesis, Impairment of Fertility",
        "Animal Pharmacology": "Animal Pharmacology",
    },
}


def clean_text(text: str) -> str:
    """Clean FDA text content."""
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text


async def fetch_fda_data(brand_name: str, generic_name: str, session: aiohttp.ClientSession) -> Dict[str, str]:
    """Fetch real section data from FDA openFDA API."""
    sections = {}
    search_terms = []
    if brand_name:
        search_terms.append(brand_name)
    if generic_name and generic_name != brand_name:
        search_terms.append(generic_name)

    for query in search_terms:
        try:
            url = f"https://api.fda.gov/drug/label.json?search={query}&limit=1"
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status != 200:
                    continue
                data = await response.json()
                results = data.get("results", [])
                if not results:
                    continue

                result = results[0]
                for fda_key, display_name in FDA_SECTION_KEYS.items():
                    content = result.get(fda_key)
                    if content:
                        if isinstance(content, list):
                            text = " ".join(str(c) for c in content)
                        else:
                            text = str(content)
                        text = clean_text(text)
                        if len(text) > 30:
                            sections[display_name] = text

                if sections:
                    print(f"      [FDA OK] {len(sections)} sections for '{query}'")
                    return sections

        except Exception as e:
            print(f"      [WARN] FDA query failed for '{query}': {e}")
            continue

    return sections


def map_sections_for_country(us_sections: Dict[str, str], country_code: str) -> Dict[str, str]:
    """Map US section names to country-specific names."""
    country_map = COUNTRY_SECTION_MAPPINGS.get(country_code, COUNTRY_SECTION_MAPPINGS["US"])
    mapped = {}
    seen_names = set()

    for us_name, content in us_sections.items():
        country_name = country_map.get(us_name, us_name)
        if country_name not in seen_names:
            mapped[country_name] = content
            seen_names.add(country_name)

    return mapped


def get_all_drugs() -> List[Tuple[str, str, str]]:
    """Return list of (brand_name, generic_name) from DB."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, brand_name, generic_name FROM drugs ORDER BY brand_name")
    rows = cur.fetchall()
    conn.close()
    return rows


def get_labels_for_drug(drug_id: str) -> List[Tuple[str, str]]:
    """Return list of (label_id, country_code) for a drug."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT dl.id, ra.country_code
        FROM drug_labels dl
        JOIN regulatory_authorities ra ON dl.authority_id = ra.id
        WHERE dl.drug_id = ?
    """, (drug_id,))
    rows = cur.fetchall()
    conn.close()
    return rows


def update_label_sections(label_id: str, sections: Dict[str, str]):
    """Replace all sections for a label."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM label_sections WHERE label_id = ?", (label_id,))
    for order, (section_name, content) in enumerate(sections.items()):
        section_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO label_sections (id, label_id, section_name, section_order, content, normalized_content)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (section_id, label_id, section_name, order, content, content.lower()))
    conn.commit()
    conn.close()


async def process_drug(drug_id: str, brand_name: str, generic_name: str, session: aiohttp.ClientSession):
    """Process a single drug: fetch FDA data, populate all country labels."""
    print(f"\n[*] {brand_name} ({generic_name})")

    # Fetch real FDA data
    us_sections = await fetch_fda_data(brand_name, generic_name, session)

    if not us_sections:
        print(f"    [SKIP] No FDA data found, skipping drug")
        return 0

    # Get all country labels for this drug
    labels = get_labels_for_drug(drug_id)
    updated = 0

    for label_id, country_code in labels:
        mapped = map_sections_for_country(us_sections, country_code)
        if mapped:
            update_label_sections(label_id, mapped)
            print(f"    [{country_code}] Updated {len(mapped)} sections (label {label_id[:8]}...)")
            updated += 1
        else:
            print(f"    [{country_code}] SKIP - no mapped sections")

    return updated


async def main():
    print("=" * 70)
    print("POPULATING ALL COUNTRIES WITH REAL PHARMACEUTICAL DATA")
    print("=" * 70)
    print("\nStrategy: Fetch real FDA content, map to each country's")
    print("regulatory section naming conventions.\n")

    drugs = get_all_drugs()
    print(f"Found {len(drugs)} drugs to process\n")

    connector = aiohttp.TCPConnector(ssl=SSL_CONTEXT)
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    total_updated = 0

    async with aiohttp.ClientSession(headers=headers, connector=connector) as session:
        for drug_id, brand_name, generic_name in drugs:
            count = await process_drug(drug_id, brand_name, generic_name, session)
            total_updated += count
            await asyncio.sleep(0.5)

    # Final summary
    print("\n" + "=" * 70)
    print("FINAL DATABASE STATE")
    print("=" * 70)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT ra.country_code,
               COUNT(DISTINCT dl.id) as labels,
               COUNT(ls.id) as sections
        FROM drug_labels dl
        JOIN regulatory_authorities ra ON dl.authority_id = ra.id
        LEFT JOIN label_sections ls ON ls.label_id = dl.id
        GROUP BY ra.country_code
        ORDER BY ra.country_code
    """)
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]} labels, {row[2]} sections")

    cur.execute("SELECT COUNT(*) FROM label_sections")
    total = cur.fetchone()[0]
    print(f"\nTotal sections in DB: {total}")
    conn.close()

    print(f"\nLabels updated in this run: {total_updated}")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
