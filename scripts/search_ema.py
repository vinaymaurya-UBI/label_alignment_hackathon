"""
European Medicines Agency (EMA) EPAR Scraper

EPAR = European Public Assessment Report
These are comprehensive regulatory documents for medicines approved through the EU centralized procedure.

Key Features:
- English language EPAR documents
- High-quality regulatory data
- PDF format for all products
- Many Gilead/Kite drugs approved

URL Pattern:
https://www.ema.europa.eu/en/medicines/human/EPAR/{drug_name}
"""

import asyncio
import aiohttp
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import re
import json
import ssl
from pathlib import Path

# SSL context
SSL_CONTEXT = ssl.create_default_context()
SSL_CONTEXT.check_hostname = False
SSL_CONTEXT.verify_mode = ssl.CERT_NONE

# EMA URLs
EMA_BASE_URL = "https://www.ema.europa.eu"
EMA_EPAR_BASE = f"{EMA_BASE_URL}/en/medicines/human/EPAR"

# Known EMA drug names (URL slugs may differ from brand names)
EMA_KNOWN_DRUGS = {
    "Genvoya": "genvoya",  # Verified - has EPAR
    "Biktarvy": "biktarvy",  # To verify
    "Descovy": "descovy",
    "Epclusa": "epclusa",
    "Veklury": "veklury",  # Remdesivir - likely has EPAR
    "Sovaldi": "sovaldi",
    "Harvoni": "harvoni",  # Another Gilead drug
    # Kite Pharma CAR-T therapies
    "Yescarta": "yescarta",
    "Tecartus": "tecartus",
}


class EMAScraper:
    """EMA EPAR scraper."""

    def __init__(self):
        self.base_url = EMA_BASE_URL
        self.epar_base = EMA_EPAR_BASE
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html',
            'Accept-Language': 'en-GB,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
        }

    async def get_epar_documents(self, drug_name_slug: str) -> Dict:
        """Get EPAR documents for a drug."""
        url = f"{self.epar_base}/{drug_name_slug}"

        print(f"    Fetching: {url}")

        try:
            connector = aiohttp.TCPConnector(ssl=SSL_CONTEXT)
            async with aiohttp.ClientSession(headers=self.headers, connector=connector) as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status != 200:
                        print(f"      [WARN] HTTP {response.status} - may not have EPAR")
                        return {}

                    html = await response.text()
                    return self._parse_epar_page(html, drug_name_slug)

        except Exception as e:
            print(f"      [ERROR] {e}")
            return {}

    def _parse_epar_page(self, html: str, drug_slug: str) -> Dict:
        """Parse EPAR page for PDF links and information."""
        soup = BeautifulSoup(html, 'html.parser')

        info = {
            'drug_slug': drug_slug,
            'url': f"{self.epar_base}/{drug_slug}",
            'epar_url': f"{self.epar_base}/{drug_slug}",
        }

        # Find all PDF links
        pdf_links = []
        for a in soup.find_all('a', href=True):
            href = a.get('href', '')
            if '.pdf' in href.lower():
                # Build full URL
                if href.startswith('/'):
                    full_url = f"{self.base_url}{href}"
                else:
                    full_url = href

                # Get the language from URL
                if '_en.pdf' in href or 'english' in href.lower():
                    pdf_links.append({
                        'url': full_url,
                        'language': 'en',
                        'type': 'EPAR English'
                    })

        info['pdf_links'] = pdf_links

        # Extract key information from page
        # Look for product name, active substance, etc.
        title = soup.find('h1')
        if title:
            info['page_title'] = title.get_text(strip=True)

        # Extract overview/description
        for div in soup.find_all('div', class_=True):
            classes = ' '.join(div.get('class', []))
            if 'overview' in classes.lower() or 'summary' in classes.lower():
                text = div.get_text(strip=True)[:500]
                info['overview'] = text
                break

        return info

    async def download_epar_pdf(self, pdf_url: str, drug_name: str) -> bytes:
        """Download EPAR PDF document."""
        try:
            connector = aiohttp.TCPConnector(ssl=SSL_CONTEXT)
            async with aiohttp.ClientSession(headers=self.headers, connector=connector) as session:
                async with session.get(pdf_url, timeout=aiohttp.ClientTimeout(total=60)) as response:
                    if response.status == 200:
                        return await response.read()
                    else:
                        print(f"      [ERROR] Failed to download PDF: HTTP {response.status}")
                        return None
        except Exception as e:
            print(f"      [ERROR] {e}")
            return None

    async def search_and_download(self, drug_name: str, drug_slug: str) -> Dict:
        """Search and download EPAR documents for a drug."""
        print(f"[*] {drug_name}")
        print(f"    Slug: {drug_slug}")

        epar_info = await self.get_epar_documents(drug_slug)

        if not epar_info:
            print(f"    [NOT FOUND] No EPAR found")
            return {}

        print(f"    [OK] Found EPAR page")
        print(f"    Title: {epar_info.get('page_title', 'N/A')[:80]}")
        print(f"    PDFs found: {len(epar_info.get('pdf_links', []))}")

        # Download English EPAR PDF
        english_epar = None
        for pdf in epar_info.get('pdf_links', []):
            if pdf.get('language') == 'en' or '_en.pdf' in pdf.get('url', ''):
                print(f"    [-] Downloading English EPAR...")
                pdf_data = await self.download_epar_pdf(pdf['url'], drug_name)

                if pdf_data:
                    # Save PDF
                    Path('data').mkdir(exist_ok=True)
                    filename = f"data/epar_{drug_name.lower()}.pdf"
                    with open(filename, 'wb') as f:
                        f.write(pdf_data)
                    print(f"    [SAVED] {filename} ({len(pdf_data)} bytes)")
                    english_epar = filename
                    break

        epar_info['local_pdf'] = english_epar
        return epar_info


async def search_all_ema_drugs():
    """Search EMA for all known drugs."""
    scraper = EMAScraper()

    print("=" * 80)
    print("EUROPEAN MEDICINES AGENCY - EPAR SEARCH")
    print("=" * 80)
    print(f"Searching for {len(EMA_KNOWN_DRUGS)} drugs...")
    print("=" * 80)

    results = {}

    for brand_name, slug in EMA_KNOWN_DRUGS.items():
        result = await scraper.search_and_download(brand_name, slug)
        results[brand_name] = result

        # Be respectful - delay between requests
        await asyncio.sleep(2)

    # Save results
    print("\n" + "=" * 80)
    print("SEARCH COMPLETE")
    print("=" * 80)

    found_count = sum(1 for r in results.values() if r.get('pdf_links'))
    print(f"\nDrugs with EPARs: {found_count}/{len(EMA_KNOWN_DRUGS)}")

    with open('data/ema_search_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: data/ema_search_results.json")

    # List downloaded PDFs
    print("\nDownloaded EPAR PDFs:")
    for drug, result in results.items():
        if result.get('local_pdf'):
            print(f"  {drug}: {result['local_pdf']}")

    return results


if __name__ == "__main__":
    asyncio.run(search_all_ema_drugs())
