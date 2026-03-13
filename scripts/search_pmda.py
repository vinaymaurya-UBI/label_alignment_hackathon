"""
PMDA (Japan) Drug Data Search
Search for Japanese package insert information
"""

import asyncio
import aiohttp
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import json
import re
import ssl

# PMDA URLs
PMDA_BASE = "https://www.pmda.go.jp"
PMDA_SEARCH = f"{PMDA_BASE}/PmdaSearch/iyakuSearch/resultList"

# Create SSL context
SSL_CONTEXT = ssl.create_default_context()
SSL_CONTEXT.check_hostname = False
SSL_CONTEXT.verify_mode = ssl.CERT_NONE

# Known approval numbers for common Gilead drugs
# These need to be verified and expanded
KNOWN_APPROVALS = {
    "GENVOYA": "25900401",
    "VEKLURY": "00700AM00606000",
    "EPCLUSA": "25900AM004016",
}

# Our 22 database drugs
DRUGS_TO_SEARCH = [
    # Gilead drugs - likely to have Japanese approvals
    "Biktarvy",
    "COMETRIQ",
    "COMPLERA",
    "Cayston",
    "DESCOVY",
    "Emtriva",
    "Epclusa",
    "Genvoya",
    "Letairis",
    "Livdelzi",
    "Sovaldi",
    "Stribild",
    "TRODELVY",
    "Truvada",
    "Tybost",
    "VEMLIDY",
    "Veklury",
    "Viread",
    "Vosevi",
    "Yeztugo",
    # Kite Pharma drugs - cell therapies, may have approvals
    "TECARTUS",
    "YESCARTA",
]


class PMDAScraper:
    """PMDA (Japan) drug data scraper."""

    def __init__(self):
        self.base_url = PMDA_BASE
        self.search_url = PMDA_SEARCH
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html',
            'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
        }

    async def search_drug(self, brand_name: str) -> List[Dict]:
        """Search PMDA for a drug by brand name."""
        print(f"  Searching: {brand_name}")

        # First check known approval numbers
        approval_num = KNOWN_APPROVALS.get(brand_name.upper())
        if approval_num:
            print(f"    Using known approval number: {approval_num}")
            return await self._get_by_approval(approval_num, brand_name)

        # Otherwise search PMDA database
        try:
            data = {
                "searchCategoryName": "医薬品名",  # Drug name in Japanese
                "keyword": brand_name,
                "searchType": "1",
                "conditionNo": "1"
            }

            connector = aiohttp.TCPConnector(ssl=SSL_CONTEXT)
            async with aiohttp.ClientSession(headers=self.headers, connector=connector) as session:
                async with session.post(
                    self.search_url,
                    data=data,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status != 200:
                        print(f"    [ERROR] HTTP {response.status}")
                        return []
                    # Try multiple encodings
                    try:
                        html = await response.text()
                    except:
                        html = await response.read()
                        html = html.decode('shift-jis', errors='ignore')

            return self._parse_search_results(html, brand_name)

        except asyncio.TimeoutError:
            print(f"    [ERROR] Request timeout")
            return []
        except Exception as e:
            print(f"    [ERROR] {e}")
            return []

    async def _get_by_approval(self, approval_num: str, brand_name: str) -> List[Dict]:
        """Get drug info by approval number."""
        pdf_url = f"{self.base_url}/PmdaSearch/iyakuDetail/ResultDetailPDF/{approval_num}.pdf"

        return [{
            'approval_number': approval_num,
            'drug_name': brand_name,
            'pdf_url': pdf_url,
            'info_url': f"{self.base_url}/PmdaSearch/iyakuDetail/ResultListPDF?seq={approval_num}"
        }]

    def _parse_search_results(self, html: str, search_term: str) -> List[Dict]:
        """Parse PMDA search results."""
        soup = BeautifulSoup(html, 'html.parser')
        results = []

        # PMDA uses tables for results
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            # Skip header row
            for row in rows[1:]:
                cols = row.find_all(['td', 'th'])
                if len(cols) >= 3:
                    approval = cols[0].text.strip()
                    name = cols[1].text.strip() if len(cols) > 1 else ""
                    company = cols[2].text.strip() if len(cols) > 2 else ""

                    # Check if name matches
                    if search_term.lower() in name.lower():
                        pdf_url = f"{self.base_url}/PmdaSearch/iyakuDetail/ResultDetailPDF/{approval}.pdf"

                        results.append({
                            'approval_number': approval,
                            'drug_name': name,
                            'company': company,
                            'pdf_url': pdf_url
                        })

        return results


async def search_all_drugs():
    """Search PMDA for all drugs."""
    scraper = PMDAScraper()

    print("=" * 80)
    print("PMDA (JAPAN) DRUG DATA SEARCH")
    print("=" * 80)
    print(f"Searching for {len(DRUGS_TO_SEARCH)} drugs...")
    print("=" * 80)
    print("\nNOTE: PMDA data is primarily in Japanese.")
    print("Package inserts are available as PDFs.")
    print("=" * 80)

    results = {}

    for drug in DRUGS_TO_SEARCH:
        print(f"\n[*] {drug}")
        search_results = await scraper.search_drug(drug)

        if search_results:
            print(f"    Found {len(search_results)} result(s)")

            for i, result in enumerate(search_results[:2]):  # Max 2
                print(f"      [{i+1}] Approval: {result['approval_number']}")
                print(f"          Name: {result['drug_name']}")
                if 'company' in result:
                    print(f"          Company: {result['company']}")
                print(f"          PDF: {result['pdf_url']}")

                results[drug] = {
                    'search_results': search_results
                }
        else:
            print(f"    [NOT FOUND] No results found")
            results[drug] = {'search_results': []}

        # Be respectful - delay between requests
        await asyncio.sleep(2)

    # Save results
    print("\n" + "=" * 80)
    print("SEARCH COMPLETE")
    print("=" * 80)

    found_count = sum(1 for r in results.values() if r['search_results'])
    print(f"\nSummary: {found_count}/{len(DRUGS_TO_SEARCH)} drugs found on PMDA")

    with open('data/pmda_search_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: data/pmda_search_results.json")

    return results


if __name__ == "__main__":
    asyncio.run(search_all_drugs())
