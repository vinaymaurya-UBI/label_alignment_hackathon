"""
EMC (Electronic Medicines Compendium) - UK Drug Data Search
Direct search and data extraction for specific drugs
"""

import asyncio
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import quote, urljoin
from typing import Dict, List, Optional
import json
import re
import ssl

# EMC base URL
EMC_BASE = "https://www.medicines.org.uk/emc"

# Create SSL context that doesn't verify (for testing only)
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


class EMCScraper:
    """EMC (UK) drug data scraper."""

    def __init__(self):
        self.base_url = EMC_BASE
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-GB,en;q=0.9',
            # Disable compression to avoid Brotli issues
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }

    async def search_drug(self, brand_name: str) -> List[Dict]:
        """Search EMC for a drug by brand name."""
        search_url = f"{self.base_url}/search?q={quote(brand_name)}"

        print(f"  Searching: {brand_name}")

        try:
            connector = aiohttp.TCPConnector(ssl=SSL_CONTEXT)
            async with aiohttp.ClientSession(headers=self.headers, connector=connector) as session:
                async with session.get(search_url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status != 200:
                        print(f"    [ERROR] HTTP {response.status}")
                        return []

                    html = await response.text()

            return self._parse_search_results(html, brand_name)

        except asyncio.TimeoutError:
            print(f"    [ERROR] Request timeout")
            return []
        except Exception as e:
            print(f"    [ERROR] {e}")
            return []

    def _parse_search_results(self, html: str, search_term: str) -> List[Dict]:
        """Parse EMC search results page."""
        soup = BeautifulSoup(html, 'html.parser')
        results = []

        # EMC search result items
        for item in soup.select('.search-result-item, .item, .result-item'):
            title_elem = (item.select_one('.search-result-title') or
                         item.select_one('h2, h3, h4') or
                         item.select_one('.title'))
            link_elem = item.select_one('a[href]')
            doc_type_elem = item.select_one('.document-type, .type')

            if title_elem and link_elem:
                title = title_elem.text.strip()
                href = link_elem.get('href', '')
                full_url = urljoin(self.base_url, href)

                # Check if this is relevant to our search
                if search_term.lower() in title.lower() or search_term.lower() in href.lower():
                    results.append({
                        'name': title,
                        'url': full_url,
                        'document_type': doc_type_elem.text.strip() if doc_type_elem else 'Unknown'
                    })

        # If standard parsing fails, try finding links in the page
        if not results:
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                text = link.text.strip()

                if '/emc/product' in href or '/emc/medicine' in href:
                    if search_term.lower() in text.lower():
                        results.append({
                            'name': text,
                            'url': urljoin(self.base_url, href),
                            'document_type': 'Product'
                        })

        return results

    async def get_product_details(self, url: str) -> Dict:
        """Get detailed product information."""
        try:
            connector = aiohttp.TCPConnector(ssl=SSL_CONTEXT)
            async with aiohttp.ClientSession(headers=self.headers, connector=connector) as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status != 200:
                        return {}

                    html = await response.text()

            soup = BeautifulSoup(html, 'html.parser')

            # Find PIL and SmPC links
            pil_link = soup.find('a', href=re.compile(r'/pil', re.I))
            smpc_link = soup.find('a', href=re.compile(r'/smpc', re.I))

            # Extract active ingredients
            active_ingredients = []
            for elem in soup.find_all(string=re.compile(r'active ingredient', re.I)):
                parent = elem.find_parent()
                if parent:
                    active_ingredients.append(parent.text.strip())

            return {
                'pil_url': urljoin(self.base_url, pil_link.get('href')) if pil_link else None,
                'smpc_url': urljoin(self.base_url, smpc_link.get('href')) if smpc_link else None,
                'active_ingredients': active_ingredients[:5],  # Limit
            }

        except Exception as e:
            print(f"    [ERROR] Getting details: {e}")
            return {}

    async def get_pil_sections(self, pil_url: str) -> Dict[str, str]:
        """Extract structured sections from PIL."""
        try:
            connector = aiohttp.TCPConnector(ssl=SSL_CONTEXT)
            async with aiohttp.ClientSession(headers=self.headers, connector=connector) as session:
                async with session.get(pil_url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status != 200:
                        return {}
                    html = await response.text()

            soup = BeautifulSoup(html, 'html.parser')
            sections = {}

            # Common PIL section headings
            section_patterns = [
                r'what.*is.*for',
                r'before.*take',
                r'how.*take',
                r'possible.*side.*effects',
                r'how.*store',
                r'contents.*pack',
                r'further.*information'
            ]

            for heading in soup.find_all(re.compile(r'h[1-6]')):
                text = heading.text.strip().lower()

                for pattern in section_patterns:
                    if re.search(pattern, text):
                        content_elem = heading.find_next_sibling()
                        if content_elem:
                            sections[heading.text.strip()] = content_elem.text.strip()[:500]
                        break

            return sections

        except Exception as e:
            print(f"    [ERROR] Getting PIL sections: {e}")
            return {}


async def search_all_drugs():
    """Search EMC for all drugs in our database."""
    scraper = EMCScraper()

    print("=" * 80)
    print("EMC (UK) DRUG DATA SEARCH")
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
                print(f"      [{i+1}] {result['name']}")
                print(f"          URL: {result['url']}")

                # Get product details
                details = await scraper.get_product_details(result['url'])
                if details.get('pil_url'):
                    print(f"          PIL: {details['pil_url']}")
                if details.get('smpc_url'):
                    print(f"          SmPC: {details['smpc_url']}")

                results[drug] = {
                    'search_results': search_results,
                    'details': details
                }
        else:
            print(f"    [NOT FOUND] No results found")
            results[drug] = {'search_results': [], 'details': {}}

        # Be respectful - delay between requests
        await asyncio.sleep(2)

    # Save results
    print("\n" + "=" * 80)
    print("SEARCH COMPLETE")
    print("=" * 80)

    # Summary
    found_count = sum(1 for r in results.values() if r['search_results'])
    print(f"\nSummary: {found_count}/{len(DRUGS_TO_SEARCH)} drugs found on EMC")

    with open('data/emc_search_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: data/emc_search_results.json")

    return results


if __name__ == "__main__":
    asyncio.run(search_all_drugs())
