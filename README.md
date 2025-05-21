# B2B Marketplace Data Analysis Tool

This project provides a comprehensive solution for gathering and analyzing data from B2B marketplaces like IndiaMART. It includes robust web scraping capabilities and advanced data analysis tools to extract meaningful insights from the collected data.

## Features

### Data Collection
- Web scraping support for IndiaMART with:
  - Robust error handling and retries
  - Rate limiting and anti-blocking measures
  - Session management
  - Rotating User-Agents
- Support for multiple product categories:
  - Industrial Machinery
  - Electronics
  - Textiles
- Automatic data backup with timestamped files

### Data Analysis
- Comprehensive Statistical Analysis:
  - Price distribution and trends
  - Geographic distribution of suppliers
  - Supplier experience analysis
  - Product category insights
  - Text analysis of product descriptions

- Advanced Visualizations:
  - Price Analysis Plots
    - Distribution histograms
    - Category-wise boxplots
    - Price vs Supplier Experience correlation
    - Regional price comparisons
  - Geographic Analysis
    - State-wise distribution
    - City-wise distribution
  - Supplier Analysis
    - Experience distribution
    - Product volume analysis
  - Word Cloud Visualization
    - Common terms in product descriptions

- Text Mining:
  - TF-IDF analysis
  - Cluster analysis of similar products
  - Keyword importance scoring

## Project Structure

```
b2b_marketplace_analysis/
├── src/
│   ├── scrapers/
│   │   ├── base_scraper.py      # Base scraping functionality
│   │   └── indiamart_scraper.py # IndiaMART specific implementation
│   ├── analysis/
│   │   └── data_analyzer.py     # Advanced data analysis tools
│   └── main.py                  # Main execution script
├── data/
│   ├── raw/                     # Raw scraped data
│   └── analysis/                # Analysis results and visualizations
├── requirements.txt
└── README.md
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd b2b_marketplace_analysis
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

To scrape data and run analysis for a specific category:

```bash
python src/main.py --category industrial_machinery
```

### Analysis Only Mode

To run analysis on existing data:

```bash
python src/main.py --category industrial_machinery --skip-scraping --input-file data/indiamart_industrial_machinery.csv
```

### Available Categories
- industrial_machinery
- electronics
- textiles

## Output Files

The tool generates several types of output:

1. Data Files:
   - Raw data: `data/indiamart_<category>.csv`
   - Backup data: `data/indiamart_<category>_YYYYMMDD_HHMMSS.csv`

2. Analysis Results:
   - Summary statistics: `data/analysis_<category>_analysis.json`
   - Price analysis: `data/analysis_<category>_price_analysis.png`
   - Geographic analysis: `data/analysis_<category>_geo_analysis.png`
   - Supplier analysis: `data/analysis_<category>_supplier_analysis.png`
   - Word cloud: `data/analysis_<category>_wordcloud.png`

3. Logs:
   - Scraping logs: `data/<category>_scraper.log`
   - Analysis logs: `data/analysis_<date>.log`
   - Main process logs: `data/main_<date>.log`

## Analysis Features

### Statistical Analysis
- Basic statistics (count, mean, median, etc.)
- Price distribution and trends
- Geographic distribution
- Supplier experience metrics
- Product categorization

### Text Analysis
- TF-IDF analysis of product descriptions
- Cluster analysis for product grouping
- Keyword importance scoring
- Word cloud visualization

### Visualization
- Interactive plots for price analysis
- Geographic distribution maps
- Supplier analysis charts
- Word clouds for common terms
