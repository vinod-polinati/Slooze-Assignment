import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Optional
import numpy as np
from pathlib import Path
import json
import logging
from datetime import datetime
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.cluster import KMeans
from wordcloud import WordCloud

class MarketplaceDataAnalyzer:
    def __init__(self, data_dir: str = 'data'):
        self.data_dir = Path(data_dir)
        self.setup_logging()
        self.data = None
        plt.style.use('seaborn-v0_8')  # Use a valid style for plots

    def setup_logging(self):
        """Configure logging for the analyzer"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'data/analysis_{datetime.now().strftime("%Y%m%d")}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('marketplace_analyzer')

    def load_data(self, filename: str) -> pd.DataFrame:
        """Load data from CSV or JSON file"""
        file_path = self.data_dir / filename
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if file_path.suffix == '.csv':
            self.data = pd.read_csv(file_path)
        elif file_path.suffix == '.json':
            self.data = pd.read_json(file_path, lines=True)
        else:
            raise ValueError("Unsupported file format. Use CSV or JSON files.")

        self.logger.info(f"Loaded {len(self.data)} records from {filename}")
        return self.data

    def clean_data(self) -> pd.DataFrame:
        """Clean and preprocess the data"""
        if self.data is None:
            raise ValueError("No data loaded. Call load_data() first.")

        # Remove duplicates
        self.data = self.data.drop_duplicates()

        # Handle missing values
        self.data = self.data.fillna({
            'title': 'Unknown',
            'location': 'Unknown',
            'specifications': {},
            'buyer_details': {}
        })

        # Extract price and other key metrics
        self.data['price_value'] = self.data.apply(self._extract_price_from_specs, axis=1)
        self.data['member_since'] = self.data.apply(self._extract_member_since, axis=1)
        self.data['product_category'] = self.data['title'].apply(self._extract_category)
        
        # Clean location data
        self.data['city'] = self.data['location'].apply(lambda x: str(x).split(',')[0].strip())
        self.data['state'] = self.data['location'].apply(lambda x: str(x).split(',')[1].strip() if len(str(x).split(',')) > 1 else 'Unknown')

        self.logger.info("Data cleaning completed")
        return self.data

    def _extract_price_from_specs(self, row: pd.Series) -> float:
        """Extract price from specifications"""
        try:
            specs = row['specifications']
            if isinstance(specs, str):
                specs = eval(specs)
            
            price_fields = ['Probable Order Value', 'Price', 'Cost', 'Value', 'Unit Price']
            for field in price_fields:
                if field in specs:
                    price_str = specs[field]
                    numbers = ''.join(filter(lambda x: x.isdigit() or x == '.', str(price_str)))
                    if numbers:
                        return float(numbers)
            return np.nan
        except:
            return np.nan

    def _extract_member_since(self, row: pd.Series) -> int:
        """Extract member duration in years"""
        try:
            buyer_details = row['buyer_details']
            if isinstance(buyer_details, str):
                buyer_details = eval(buyer_details)
            
            if 'member_since' in buyer_details:
                year_str = str(buyer_details['member_since'])
                if year_str.isdigit():
                    return datetime.now().year - int(year_str)
            return np.nan
        except:
            return np.nan

    def _extract_category(self, title: str) -> str:
        """Extract product category from title"""
        common_categories = ['Machine', 'Equipment', 'System', 'Tool', 'Device', 'Component']
        for category in common_categories:
            if category.lower() in title.lower():
                return category
        return 'Other'

    def generate_summary_statistics(self) -> Dict:
        """Generate comprehensive summary statistics"""
        if self.data is None:
            raise ValueError("No data loaded. Call load_data() first.")

        # Convert tuple keys to strings in the groupby results
        by_category = self.data.groupby('product_category')['price_value'].agg(['mean', 'median', 'count'])
        by_category_dict = {
            str(k): {
                'mean': float(v['mean']),
                'median': float(v['median']),
                'count': int(v['count'])
            }
            for k, v in by_category.iterrows()
        }

        # Convert tuple keys to strings in location groupby
        products_by_location = self.data.groupby(['state', 'city']).size()
        location_dict = {
            f"{state}_{city}": count 
            for (state, city), count in products_by_location.items()
        }

        summary = {
            'overview': {
                'total_products': len(self.data),
                'unique_locations': self.data['location'].nunique(),
                'unique_cities': self.data['city'].nunique(),
                'unique_states': self.data['state'].nunique(),
                'total_suppliers': self.data['member_since'].count()
            },
            'price_analysis': {
                'statistics': self.data['price_value'].dropna().describe().to_dict(),
                'by_category': by_category_dict
            },
            'geographical_insights': {
                'top_cities': self.data['city'].value_counts().head(10).to_dict(),
                'top_states': self.data['state'].value_counts().head(10).to_dict(),
                'products_per_location': location_dict
            },
            'supplier_analysis': {
                'member_duration_stats': self.data['member_since'].describe().to_dict(),
                'products_per_supplier': self.data.groupby('member_since').size().to_dict()
            },
            'product_insights': {
                'category_distribution': self.data['product_category'].value_counts().to_dict(),
                'top_products': self.data['title'].value_counts().head(10).to_dict()
            }
        }

        self.logger.info("Generated comprehensive summary statistics")
        return summary

    def plot_price_analysis(self, save_path: Optional[str] = None):
        """Generate comprehensive price analysis plots"""
        fig = plt.figure(figsize=(20, 15))
        
        # Price distribution
        plt.subplot(2, 2, 1)
        sns.histplot(data=self.data.dropna(subset=['price_value']), x='price_value', bins=50)
        plt.title('Price Distribution')
        plt.xlabel('Price')
        
        # Price by category boxplot
        plt.subplot(2, 2, 2)
        sns.boxplot(data=self.data.dropna(subset=['price_value']), x='product_category', y='price_value')
        plt.xticks(rotation=45)
        plt.title('Price Distribution by Category')
        
        # Price vs Member Duration scatter
        plt.subplot(2, 2, 3)
        sns.scatterplot(data=self.data.dropna(subset=['price_value', 'member_since']), 
                       x='member_since', y='price_value', alpha=0.5)
        plt.title('Price vs Supplier Experience')
        
        # Average price by state
        plt.subplot(2, 2, 4)
        state_prices = self.data.groupby('state')['price_value'].mean().sort_values(ascending=False).head(10)
        sns.barplot(x=state_prices.values, y=state_prices.index)
        plt.title('Average Price by State (Top 10)')
        
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path)
            plt.close()
        else:
            plt.show()

    def plot_geographical_analysis(self, save_path: Optional[str] = None):
        """Generate geographical analysis plots"""
        fig = plt.figure(figsize=(20, 10))
        
        # Products by state
        plt.subplot(1, 2, 1)
        state_counts = self.data['state'].value_counts().head(10)
        sns.barplot(x=state_counts.values, y=state_counts.index)
        plt.title('Number of Products by State (Top 10)')
        
        # Products by city
        plt.subplot(1, 2, 2)
        city_counts = self.data['city'].value_counts().head(10)
        sns.barplot(x=city_counts.values, y=city_counts.index)
        plt.title('Number of Products by City (Top 10)')
        
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path)
            plt.close()
        else:
            plt.show()

    def plot_supplier_analysis(self, save_path: Optional[str] = None):
        """Generate supplier analysis plots"""
        fig = plt.figure(figsize=(20, 10))
        
        # Member duration distribution
        plt.subplot(1, 2, 1)
        sns.histplot(data=self.data.dropna(subset=['member_since']), x='member_since', bins=20)
        plt.title('Supplier Experience Distribution')
        plt.xlabel('Years as Member')
        
        # Products per supplier experience level
        plt.subplot(1, 2, 2)
        supplier_exp = self.data.groupby('member_since').size()
        sns.barplot(x=supplier_exp.index, y=supplier_exp.values)
        plt.title('Number of Products by Supplier Experience')
        plt.xlabel('Years as Member')
        
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path)
            plt.close()
        else:
            plt.show()

    def generate_wordcloud(self, save_path: Optional[str] = None):
        """Generate word cloud from product titles and specifications"""
        text_data = ' '.join(self.data['title'].fillna('') + ' ' + 
                           self.data['specifications'].apply(str))
        
        wordcloud = WordCloud(width=1200, height=800, 
                            background_color='white',
                            max_words=100).generate(text_data)
        
        plt.figure(figsize=(15, 10))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title('Most Common Terms in Products')
        
        if save_path:
            plt.savefig(save_path)
            plt.close()
        else:
            plt.show()

    def analyze_text_data(self) -> Dict:
        """Perform comprehensive text analysis"""
        # Combine title and specifications for analysis
        text_data = self.data['title'].fillna('') + ' ' + self.data['specifications'].apply(str)
        
        # TF-IDF analysis
        tfidf = TfidfVectorizer(stop_words='english', max_features=100)
        tfidf_matrix = tfidf.fit_transform(text_data)
        
        # Get top terms by TF-IDF score
        feature_names = tfidf.get_feature_names_out()
        tfidf_scores = pd.DataFrame(
            tfidf_matrix.mean(axis=0).T,
            index=feature_names,
            columns=['importance']
        ).sort_values('importance', ascending=False)

        # Cluster analysis
        n_clusters = min(5, len(self.data))
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        clusters = kmeans.fit_predict(tfidf_matrix)
        
        # Get top terms per cluster
        cluster_terms = {}
        for i in range(n_clusters):
            cluster_docs = tfidf_matrix[clusters == i]
            if cluster_docs.shape[0] > 0:
                top_terms_idx = cluster_docs.mean(axis=0).argsort()[0, -10:][0]
                cluster_terms[f'cluster_{i}'] = [feature_names[idx] for idx in top_terms_idx]

        return {
            'top_terms': tfidf_scores.head(20).to_dict()['importance'],
            'clusters': cluster_terms,
            'cluster_sizes': pd.Series(clusters).value_counts().to_dict()
        }

    def save_analysis_results(self, results: Dict, filename: str):
        """Save analysis results to a file"""
        output_path = self.data_dir / filename
        
        # Convert numpy types to Python native types
        def convert_to_native(obj):
            if isinstance(obj, dict):
                return {k: convert_to_native(v) for k, v in obj.items()}
            elif isinstance(obj, (list, tuple)):
                return [convert_to_native(x) for x in obj]
            elif isinstance(obj, (np.int_, np.intc, np.intp, np.int8, np.int16, np.int32,
                               np.int64, np.uint8, np.uint16, np.uint32, np.uint64)):
                return int(obj)
            elif isinstance(obj, (np.float_, np.float16, np.float32, np.float64)):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            return obj
        
        results = convert_to_native(results)
        
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        self.logger.info(f"Saved analysis results to {filename}")

    def run_full_analysis(self, input_file: str, output_prefix: str):
        """Run complete analysis pipeline"""
        # Load and clean data
        self.load_data(input_file)
        self.clean_data()

        # Generate analysis results
        results = {
            'summary_statistics': self.generate_summary_statistics(),
            'text_analysis': self.analyze_text_data()
        }

        # Save results
        self.save_analysis_results(results, f"{output_prefix}_analysis.json")

        # Generate and save plots
        self.plot_price_analysis(f"{self.data_dir}/{output_prefix}_price_analysis.png")
        self.plot_geographical_analysis(f"{self.data_dir}/{output_prefix}_geo_analysis.png")
        self.plot_supplier_analysis(f"{self.data_dir}/{output_prefix}_supplier_analysis.png")
        self.generate_wordcloud(f"{self.data_dir}/{output_prefix}_wordcloud.png")

        self.logger.info("Completed full analysis") 