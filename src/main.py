import argparse
from scrapers.indiamart_scraper import IndiaMartScraper
from analysis.data_analyzer import MarketplaceDataAnalyzer
import logging
from datetime import datetime
import sys

def setup_logging():
    """Configure logging for the main script"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f'data/main_{datetime.now().strftime("%Y%m%d")}.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger('main')

def main():
    parser = argparse.ArgumentParser(description='B2B Marketplace Data Analysis Tool')
    parser.add_argument('--category', type=str, required=True,
                      choices=['industrial_machinery', 'electronics', 'textiles'],
                      help='Category to scrape from IndiaMART')
    parser.add_argument('--skip-scraping', action='store_true',
                      help='Skip scraping and only run analysis on existing data')
    parser.add_argument('--input-file', type=str,
                      help='Input file for analysis (required if skip-scraping is True)')
    
    args = parser.parse_args()
    logger = setup_logging()

    try:
        # Scraping phase
        if not args.skip_scraping:
            logger.info(f"Starting scraping for category: {args.category}")
            scraper = IndiaMartScraper(args.category)
            scraper.run()
            input_file = f"indiamart_{args.category}.csv"
        else:
            if not args.input_file:
                logger.error("Input file is required when skip-scraping is True")
                sys.exit(1)
            input_file = args.input_file

        # Analysis phase
        logger.info("Starting data analysis")
        analyzer = MarketplaceDataAnalyzer()
        analyzer.run_full_analysis(input_file, f"analysis_{args.category}")
        
        logger.info("Process completed successfully")

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 