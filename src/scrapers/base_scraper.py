from abc import ABC, abstractmethod
import logging
import time
from typing import Dict, List, Optional
import random
from fake_useragent import UserAgent
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os

class BaseScraper(ABC):
    def __init__(self, base_url: str, category: str):
        self.base_url = base_url
        self.category = category
        self.user_agent = UserAgent()
        self.session = self._create_session()
        self.setup_logging()
        
    def setup_logging(self):
        """Configure logging for the scraper"""
        # Ensure data directory exists
        os.makedirs('data', exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'data/{self.category}_scraper.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(f"{self.category}_scraper")

    def _create_session(self) -> requests.Session:
        """Create a requests session with retry mechanism"""
        session = requests.Session()
        
        # Configure retry strategy
        retries = requests.adapters.Retry(
            total=5,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504]
        )
        
        # Mount the retry adapter
        adapter = requests.adapters.HTTPAdapter(max_retries=retries)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        
        return session

    def rotate_user_agent(self):
        """Rotate the User-Agent header"""
        self.session.headers.update({'User-Agent': self.user_agent.random})

    def save_to_csv(self, data: List[Dict], filename: str):
        """Save scraped data to CSV file"""
        if not data:
            self.logger.warning("No data to save")
            return

        try:
            df = pd.DataFrame(data)
            # Save with timestamp for backup
            backup_file = f'data/{filename}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            df.to_csv(backup_file, index=False)
            self.logger.info(f"Backup saved to {backup_file}")
            
            # Save with fixed filename for analysis
            output_file = f'data/{filename}.csv'
            df.to_csv(output_file, index=False)
            self.logger.info(f"Data saved to {output_file}")
        except Exception as e:
            self.logger.error(f"Error saving data to CSV: {str(e)}")

    @abstractmethod
    def scrape_products(self) -> List[Dict]:
        """Scrape products from the website. Must be implemented by child classes."""
        pass

    def run(self):
        """Run the scraper and save results"""
        self.logger.info(f"Starting {self.__class__.__name__} for category: {self.category}")
        products = self.scrape_products()
        
        if products:
            self.save_to_csv(products, f"indiamart_{self.category}")
            self.logger.info(f"Successfully scraped {len(products)} products")
        else:
            self.logger.warning("No products were scraped")

    def get_headers(self) -> Dict[str, str]:
        """Generate random headers for requests"""
        return {
            'User-Agent': self.user_agent.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }

    def make_request(self, url: str, headers: Dict = None, retries: int = 3) -> Optional[BeautifulSoup]:
        """Make an HTTP request with retry logic and return BeautifulSoup object"""
        if headers is None:
            headers = self.get_headers()
        else:
            # Merge custom headers with default headers
            default_headers = self.get_headers()
            default_headers.update(headers)
            headers = default_headers

        for attempt in range(retries):
            try:
                self.logger.debug(f"Making request to {url} (attempt {attempt + 1}/{retries})")
                response = self.session.get(
                    url, 
                    headers=headers,
                    timeout=30,
                    allow_redirects=True
                )
                response.raise_for_status()
                
                # Check if we got a valid HTML response
                content_type = response.headers.get('content-type', '').lower()
                if 'text/html' not in content_type:
                    self.logger.error(f"Unexpected content type: {content_type}")
                    return None

                time.sleep(random.uniform(1, 3))  # Random delay between requests
                return BeautifulSoup(response.text, 'html.parser')
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Error fetching {url}: {str(e)}")
                if attempt == retries - 1:
                    return None
                time.sleep(random.uniform(5, 10))  # Longer delay between retries
            except Exception as e:
                self.logger.error(f"Unexpected error while fetching {url}: {str(e)}")
                if attempt == retries - 1:
                    return None
                time.sleep(random.uniform(5, 10))

    def save_to_json(self, data: List[Dict], filename: str):
        """Save scraped data to JSON file"""
        if not data:
            self.logger.warning("No data to save to JSON")
            return
            
        # Ensure data directory exists
        os.makedirs('data', exist_ok=True)
        
        df = pd.DataFrame(data)
        df['timestamp'] = datetime.now()
        
        # Save with timestamp for backup
        backup_file = f'data/{filename}_{datetime.now().strftime("%Y%m%d")}.json'
        df.to_json(backup_file, orient='records', lines=True)
        self.logger.info(f"Backup saved to {backup_file}")
        
        # Save with fixed filename for analysis
        output_file = f'data/{filename}.json'
        df.to_json(output_file, orient='records', lines=True)
        self.logger.info(f"Data saved to {output_file}") 