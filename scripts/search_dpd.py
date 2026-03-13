"""
Health Canada DPD (Drug Product Database) Search
Direct search for Canadian drug data
"""

import asyncio
import aiohttp
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import json
import re
import ssl

# DPD URLs
DPD_SEARCH_URL = "https://health-products.canada.ca/dpd-bdpp/index-eng.jsp"
DPD_INFO_BASE = "https://health-products.canada.ca/dpd-bdpp/info.do"

# Create SSL context
SSL_CONTEXT = ssl.create_default_context()
SSL_CONTEXT.check_hostname = False
SSL_CONTEXT.verify_mode = ssl.CERT_NONE

# Our 22 database drugs
DRUGS_TO_SEARCH = [
    # Gilead drugs
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
    # Kite Pharma drugs
    "TECARTUS",
    "YESCARTA",
]


class HealthCanadaScraper:
    """Health Canada DPD scraper."""

    def __init__(self):
        self.search_url = DPD_SEARCH_URL
        self.info_base = DPD_INFO_BASE
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml',
            'Accept-Language': 'en-CA,en;q=0.9',
        }

    async def search_drug(self, brand_name: str) -> List[Dict]:
        """Search DPD for a drug by brand name."""
        print(f"  Searching: {brand_name}")

        try:
            # DPD uses POST requests for search
            data = {
                "searchType": "brandName",
                "input": brand_name,
                "lang": "eng",
                "search": "Search"
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

                    html = await response.text(errors='ignore')

            return self._parse_dpd_results(html, brand_name)

        except asyncio.TimeoutError:
            print(f"    [ERROR] Request timeout")
            return []
        except Exception as e:
            print(f"    [ERROR] {e}")
            return []

    def _parse_dpd_results(self, html: str, search_term: str) -> List[Dict]:
        """Parse DPD search results."""
        soup = BeautifulSoup(html, 'html.parser')
        results = []

        # DPD uses tables for results
        tables = soup.find_all('table')
        for table in tables:
            for row in table.find_all('tr'):
                cols = row.find_all('td')
                if len(cols) >= 3:
                    # First column is usually DIN
                    din = cols[0].text.strip()

                    # Check if DIN format (8-10 digits)
                    if not re.match(r'^\d{5,10}$', din):
                        continue

                    # Brand name is usually second column
                    brand = cols[1].text.strip() if len(cols) > 1 else ""
                    strength = cols[2].text.strip() if len(cols) > 2 else ""

                    # Match search term
                    if search_term.lower() in brand.lower():
                        results.append({
                            'din': din,
                            'brand_name': brand,
                            'strength': strength,
                            'info_url': f"{self.info_base}?code={din}"
                        })

        return results

    async def get_product_info(self, din: str) -> Dict:
        """Get detailed product info by DIN."""
        url = f"{self.info_base}?code={din}"

        try:
            connector = aiohttp.TCPConnector(ssl=SSL_CONTEXT)
            async with aiohttp.ClientSession(headers=self.headers, connector=connector) as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status != 200:
                        return {}
                    html = await response.text(errors='ignore')

            soup = BeautifulSoup(html, 'html.parser')
            info = {}

            # Extract product information
            tables = soup.find_all('table')
            for table in tables:
                for row in table.find_all('tr'):
                    cols = row.find_all(['td', 'th'])
                    if len(cols) >= 2:
                        label = cols[0].text.strip()
                        value = cols[1].text.strip()

                        if label and value:
                            info[label] = value

            return info

        except Exception as e:
            print(f"    [ERROR] Getting product info: {e}")
            return {}


async def search_all_drugs():
    """Search Health Canada DPD for all drugs."""
    scraper = HealthCanadaScraper()

    print("=" * 80)
    print("HEALTH CANADA DPD DRUG SEARCH")
    print("=" * 80)
    print(f"Searching for {len(DRUGS_TO_SEARCH)} drugs...")
    print("=" * 80)

    results = {}

    for drug in DRUGS_TO_SEARCH:
        print(f"\n[*] {drug}")
        search_results = await scraper.search_drug(drug)

        if search_results:
            print(f"    Found {len(search_results)} result(s)")

            for i, result in enumerate(search_results[:3]):  # Max 3
                print(f"      [{i+1}] DIN: {result['din']}")
                print(f"          Brand: {result['brand_name']}")
                print(f"          Strength: {result['strength']}")

                # Get detailed info
                info = await scraper.get_product_info(result['din'])
                if info:
                    manufacturer = info.get('Manufacturer', 'N/A')
                    schedule = info.get('Schedule', 'N/A')
                    print(f"          Manufacturer: {manufacturer}")
                    print(f"          Schedule: {schedule}")

                results[drug] = {
                    'search_results': search_results,
                    'product_info': info
                }
        else:
            print(f"    [NOT FOUND] No results found")
            results[drug] = {'search_results': [], 'product_info': {}}

        # Be respectful - delay between requests
        await asyncio.sleep(2)

    # Save results
    print("\n" + "=" * 80)
    print("SEARCH COMPLETE")
    print("=" * 80)

    found_count = sum(1 for r in results.values() if r['search_results'])
    print(f"\nSummary: {found_count}/{len(DRUGS_TO_SEARCH)} drugs found in DPD")

    with open('data/dpd_search_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: data/dpd_search_results.json")

    return results


if __name__ == "__main__":
    asyncio.run(search_all_drugs())
