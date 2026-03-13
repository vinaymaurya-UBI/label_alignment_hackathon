"""
Australia TGA (Therapeutic Goods Administration) Data Scraper

The Australian Register of Therapeutic Goods (ARTG) is a comprehensive database
of all therapeutic goods available in Australia.

Key Features:
- Publicly searchable database
- English language documentation
- Product Information (PI) documents available
- Many Gilead/Kite/Exelixis drugs approved

Data Sources:
1. ARTG Search: https://tga-search.clients.funnelback.com/tga/search/
2. TGA Website: https://www.tga.gov.au/
3. Public ARTG Summary: https://www.tga.gov.au/browse/australian-register-therapeutic-goods

Drug Coverage (Expected):
- Genvoya: Likely approved
- Biktarvy: Likely approved
- DESCOVY: Likely approved
- Epclusa: Likely approved
- Sovaldi: Likely approved
- Veklury: Likely approved
- TECARTUS: Possibly approved
- YESCARTA: Possibly approved
- COMETRIQ: Possibly approved
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

# TGA ARTG Search URL
TGA_SEARCH_URL = "https://tga-search.clients.funnelback.com/tga/search"
TGA_BASE_URL = "https://www.tga.gov.au"

# Our 22 database drugs to search for
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


class TGAScraper:
    """Therapeutic Goods Administration (Australia) scraper."""

    def __init__(self):
        self.base_url = TGA_BASE_URL
        self.search_url = TGA_SEARCH_URL
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html',
            'Accept-Language': 'en-AU,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
        }

    async def search_drug(self, brand_name: str) -> List[Dict]:
        """Search TGA ARTG for a drug by brand name."""
        print(f"  Searching: {brand_name}")

        # TGA uses a Funnelback search API
        search_params = {
            'query': brand_name,
            'form': 'json',
            'collection': 'tga-web',
            'profile': 'tga',
        }

        try:
            connector = aiohttp.TCPConnector(ssl=SSL_CONTEXT)
            async with aiohttp.ClientSession(headers=self.headers, connector=connector) as session:
                async with session.get(
                    self.search_url,
                    params=search_params,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status != 200:
                        print(f"    [ERROR] HTTP {response.status}")
                        return []

                    data = await response.json()
                    return self._parse_search_results(data, brand_name)

        except asyncio.TimeoutError:
            print(f"    [ERROR] Request timeout")
            return []
        except Exception as e:
            print(f"    [ERROR] {e}")
            return []

    def _parse_search_results(self, data: Dict, search_term: str) -> List[Dict]:
        """Parse TGA search results."""
        results = []

        # Funnelback returns results in a specific format
        if 'results' not in data:
            return results

        for result in data.get('results', []):
            # Check if this is a medicine/therapeutic good
            if result.get('metaData', {}).get('type') != 'ARTG Entry':
                continue

            title = result.get('title', '')
            url = result.get('clickTrackingUrl', '')
            summary = result.get('summary', '')

            # Extract ARTG number from URL or summary
            artg_number = self._extract_artg_number(title + ' ' + summary + ' ' + url)

            # Check if search term matches
            if search_term.lower() in title.lower() or search_term.lower() in summary.lower():
                results.append({
                    'name': title,
                    'url': url,
                    'artg_number': artg_number,
                    'summary': summary[:200] if summary else '',
                })

        return results

    def _extract_artg_number(self, text: str) -> Optional[str]:
        """Extract ARTG number from text."""
        # ARTG numbers are typically 8-9 digits
        match = re.search(r'\b\d{8,9}\b', text)
        return match.group(0) if match else None

    async def get_product_details(self, artg_number: str) -> Dict:
        """Get detailed product information from TGA by ARTG number."""
        # Construct the ARTG URL
        url = f"{self.base_url}/products/artg-{artg_number}"

        try:
            connector = aiohttp.TCPConnector(ssl=SSL_CONTEXT)
            async with aiohttp.ClientSession(headers=self.headers, connector=connector) as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status != 200:
                        return {}

                    html = await response.text()
                    return self._parse_product_page(html, artg_number)

        except Exception as e:
            print(f"      [ERROR] Getting details: {e}")
            return {}

    def _parse_product_page(self, html: str, artg_number: str) -> Dict:
        """Parse TGA product page for details."""
        soup = BeautifulSoup(html, 'html.parser')

        # Extract product information
        info = {
            'artg_number': artg_number,
            'url': f"{self.base_url}/products/artg-{artg_number}",
        }

        # Look for Product Information (PI) link
        pi_link = None
        for a in soup.find_all('a', href=True):
            href = a.get('href', '')
            text = a.get_text(strip=True).lower()

            if 'product information' in text or 'pi' in text or 'artg' in href:
                if href.startswith('/'):
                    pi_link = f"{self.base_url}{href}"
                elif href.startswith('http'):
                    pi_link = href
                break

        if pi_link:
            info['pi_url'] = pi_link

        # Extract basic info from page
        # Look for sponsor, active ingredients, etc.
        for div in soup.find_all('div', class_=True):
            classes = ' '.join(div.get('class', []))
            if 'product' in classes.lower() or 'medicine' in classes.lower():
                text = div.get_text(strip=True)[:500]
                if text and len(text) > 20:
                    info['details'] = text
                    break

        return info


async def search_all_tga_drugs():
    """Search TGA ARTG for all drugs."""
    scraper = TGAScraper()

    print("=" * 80)
    print("AUSTRALIA TGA ARTG DRUG SEARCH")
    print("=" * 80)
    print(f"Searching for {len(DRUGS_TO_SEARCH)} drugs...")
    print("=" * 80)

    results = {}

    for drug in DRUGS_TO_SEARCH:
        print(f"\n[*] {drug}")
        search_results = await scraper.search_drug(drug)

        if search_results:
            print(f"    Found {len(search_results)} result(s)")

            for i, result in enumerate(search_results[:3]):
                print(f"      [{i+1}] {result['name'][:80]}")
                print(f"          ARTG: {result.get('artg_number', 'N/A')}")
                print(f"          URL: {result.get('url', 'N/A')[:80]}")

                # Get product details if ARTG number available
                artg_num = result.get('artg_number')
                if artg_num:
                    details = await scraper.get_product_details(artg_num)
                    if details.get('pi_url'):
                        print(f"          PI: {details['pi_url']}")

                results[drug] = {
                    'search_results': search_results,
                    'product_details': details if artg_num else {}
                }
        else:
            print(f"    [NOT FOUND] No results found")
            results[drug] = {'search_results': [], 'product_details': {}}

        # Be respectful - delay between requests
        await asyncio.sleep(2)

    # Save results
    print("\n" + "=" * 80)
    print("SEARCH COMPLETE")
    print("=" * 80)

    found_count = sum(1 for r in results.values() if r['search_results'])
    print(f"\nSummary: {found_count}/{len(DRUGS_TO_SEARCH)} drugs found on TGA ARTG")

    with open('data/tga_search_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: data/tga_search_results.json")

    return results


if __name__ == "__main__":
    asyncio.run(search_all_tga_drugs())
