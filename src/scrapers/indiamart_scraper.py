from typing import Dict, List
from bs4 import BeautifulSoup
import re
from .base_scraper import BaseScraper
import time
import json
import requests

class IndiaMartScraper(BaseScraper):
    def __init__(self, category: str):
        super().__init__('https://trade.indiamart.com', category)
        self.category_urls = {
            'industrial_machinery': '/offer/plant-machinery/',
            'electronics': '/offer/electronics-electrical/',
            'textiles': '/offer/textiles-leather/'
        }
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }

    def scrape_products(self) -> List[Dict]:
        """Scrape product listings from IndiaMART."""
        products = []
        page = 1
        max_pages = 5  # Limit to 5 pages for testing

        while page <= max_pages:
            url = f"{self.base_url}{self.category_urls[self.category]}?page={page}"
            self.logger.info(f"Scraping page {page}: {url}")

            try:
                response = self.session.get(url, headers=self.headers, timeout=30)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')

                # Find all product listings
                listings = soup.find_all('div', class_='srdiv')
                
                if not listings:
                    self.logger.warning(f"No listings found on page {page}")
                    break

                for listing in listings:
                    try:
                        # Extract product details
                        title = listing.find('a', class_='clst')
                        title_text = title.text.strip() if title else None

                        # Extract location
                        location_elem = listing.find('p', class_='bl_dtt', string=lambda x: x and not x.startswith('mins ago'))
                        location = location_elem.text.strip() if location_elem else None

                        # Extract buyer details
                        buyer_details = {}
                        buyer_div = listing.find('div', class_='bpDiv')
                        if buyer_div:
                            member_since = buyer_div.find('td', class_='bpValue')
                            buyer_details['member_since'] = member_since.text.strip() if member_since else None

                        # Extract specifications
                        specs = {}
                        spec_rows = listing.find_all('tr')
                        for row in spec_rows:
                            key = row.find('td', class_='addinfo')
                            value = row.find('td', class_='addinfo2')
                            if key and value:
                                key_text = key.text.strip().rstrip(':')
                                specs[key_text] = value.text.strip()

                        product = {
                            'title': title_text,
                            'location': location,
                            'buyer_details': buyer_details,
                            'specifications': specs,
                            'source_url': url
                        }
                        products.append(product)

                    except Exception as e:
                        self.logger.error(f"Error parsing listing: {str(e)}")
                        continue

                # Add delay between pages
                time.sleep(2)
                page += 1

            except requests.RequestException as e:
                self.logger.error(f"Error making request: {str(e)}")
                break

        if not products:
            self.logger.warning("No products were scraped")

        return products 