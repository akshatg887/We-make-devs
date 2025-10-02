import pandas as pd
from typing import List, Dict, Any
import json
from datetime import datetime

class DataProcessor:
    @staticmethod
    def process_places_data(places_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process and analyze Google Places data with advanced metrics"""
        if not places_data:
            return {}
        
        df = pd.DataFrame(places_data)
        
        # Basic metrics
        analysis = {
            "total_businesses": len(df),
            "data_quality": "high" if len(df) > 10 else "medium" if len(df) > 5 else "low",
            "collection_timestamp": datetime.now().isoformat()
        }
        
        # Rating analysis
        if 'rating' in df.columns:
            rating_data = df['rating'].dropna()
            if len(rating_data) > 0:
                analysis.update({
                    "average_rating": round(rating_data.mean(), 2),
                    "rating_std": round(rating_data.std(), 2),
                    "min_rating": round(rating_data.min(), 2),
                    "max_rating": round(rating_data.max(), 2),
                    "rating_distribution": rating_data.value_counts().sort_index().to_dict(),
                    "excellent_businesses": len(rating_data[rating_data >= 4.5]),
                    "poor_businesses": len(rating_data[rating_data <= 3.0])
                })
        
        # Price level analysis
        if 'priceLevel' in df.columns:
            price_data = df['priceLevel'].dropna()
            if len(price_data) > 0:
                analysis["price_level_distribution"] = price_data.value_counts().sort_index().to_dict()
                analysis["average_price_level"] = round(price_data.mean(), 2)
        
        # Review volume analysis
        if 'user_ratings_total' in df.columns:
            review_data = df['user_ratings_total'].dropna()
            if len(review_data) > 0:
                analysis.update({
                    "total_reviews": int(review_data.sum()),
                    "average_reviews_per_business": round(review_data.mean(), 2),
                    "most_reviewed": int(review_data.max()) if len(review_data) > 0 else 0
                })
        
        # Category analysis
        if 'types' in df.columns:
            all_categories = []
            for categories in df['types'].dropna():
                if isinstance(categories, list):
                    all_categories.extend(categories)
            
            if all_categories:
                category_counts = pd.Series(all_categories).value_counts()
                analysis["top_categories"] = category_counts.head(10).to_dict()
                analysis["unique_categories"] = len(category_counts)
        
        # Location density analysis (if coordinates available)
        if 'latitude' in df.columns and 'longitude' in df.columns:
            coords_df = df[['latitude', 'longitude']].dropna()
            if len(coords_df) > 1:
                analysis["geographic_spread"] = DataProcessor._calculate_geographic_spread(coords_df)
        
        return analysis
    
    @staticmethod
    def process_trends_data(trends_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process and analyze Google Trends data"""
        if not trends_data:
            return {}
        
        df = pd.DataFrame(trends_data)
        
        analysis = {
            "total_trends_points": len(df),
            "data_quality": "high" if len(df) > 5 else "medium" if len(df) > 2 else "low"
        }
        
        # Time-based trend analysis
        if 'date' in df.columns and 'value' in df.columns:
            time_series = df[['date', 'value']].dropna()
            if len(time_series) > 0:
                # Convert to time series analysis
                time_series['date'] = pd.to_datetime(time_series['date'])
                time_series = time_series.sort_values('date')
                
                analysis["interest_over_time"] = {
                    str(row['date'].date()): row['value'] 
                    for _, row in time_series.iterrows()
                }
                
                # Trend calculations
                values = time_series['value'].tolist()
                if len(values) > 1:
                    analysis.update({
                        "trend_growth_rate": ((values[-1] - values[0]) / values[0] * 100) if values[0] != 0 else 0,
                        "average_interest": round(sum(values) / len(values), 2),
                        "peak_interest": max(values),
                        "recent_momentum": DataProcessor._calculate_momentum(values[-5:]) if len(values) >= 5 else 0
                    })
        
        # Keyword analysis
        if 'query' in df.columns:
            keyword_data = df['query'].dropna()
            if len(keyword_data) > 0:
                analysis["trending_keywords"] = keyword_data.value_counts().head(15).to_dict()
                analysis["total_unique_keywords"] = len(keyword_data.unique())
        
        # Related queries analysis
        if 'relatedQueries' in df.columns:
            related_queries = []
            for queries in df['relatedQueries'].dropna():
                if isinstance(queries, list):
                    related_queries.extend(queries)
            
            if related_queries:
                analysis["related_queries"] = pd.Series(related_queries).value_counts().head(10).to_dict()
        
        return analysis
    
    @staticmethod
    def _calculate_geographic_spread(coords_df: pd.DataFrame) -> Dict:
        """Calculate geographic spread of businesses"""
        try:
            lat_range = coords_df['latitude'].max() - coords_df['latitude'].min()
            lon_range = coords_df['longitude'].max() - coords_df['longitude'].min()
            
            return {
                "lat_range_degrees": round(lat_range, 4),
                "lon_range_degrees": round(lon_range, 4),
                "spread_indicator": "concentrated" if max(lat_range, lon_range) < 0.1 else "dispersed"
            }
        except:
            return {"spread_indicator": "unknown"}
    
    @staticmethod
    def _calculate_momentum(values: List[float]) -> float:
        """Calculate momentum of recent trend values"""
        if len(values) < 2:
            return 0
        
        # Simple momentum calculation
        recent_avg = sum(values[-3:]) / 3
        previous_avg = sum(values[:3]) / 3 if len(values) >= 6 else values[0]
        
        return ((recent_avg - previous_avg) / previous_avg * 100) if previous_avg != 0 else 0