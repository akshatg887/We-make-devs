import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from typing import List, Dict, Any
import os

class VisualizationGenerator:
    def __init__(self):
        plt.style.use('default')
        self.output_dir = "visualizations"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_visualizations(self, insights: str, business_type: str, location: str) -> List[str]:
        """Generate various visualizations based on insights"""
        visualizations = []
        
        try:
            # Market saturation chart
            sat_chart = self._create_market_saturation_chart(business_type, location)
            visualizations.append(sat_chart)
            
            # Trend analysis chart
            trend_chart = self._create_trend_analysis_chart(business_type, location)
            visualizations.append(trend_chart)
            
            # Competitive landscape
            comp_chart = self._create_competitive_landscape(business_type, location)
            visualizations.append(comp_chart)
            
        except Exception as e:
            print(f"Visualization generation error: {e}")
        
        return visualizations
    
    def _create_market_saturation_chart(self, business_type: str, location: str) -> str:
        """Create market saturation visualization"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Sample data - in real implementation, this would come from scraped data
        categories = ['Low Competition', 'Medium Competition', 'High Competition']
        values = [30, 45, 25]  # These would be calculated from actual data
        
        ax.bar(categories, values, color=['green', 'orange', 'red'])
        ax.set_title(f'Market Saturation Analysis: {business_type} in {location}')
        ax.set_ylabel('Percentage (%)')
        
        filename = os.path.join(self.output_dir, f'market_saturation_{business_type}_{location}.png')
        plt.savefig(filename)
        plt.close()
        
        return filename
    
    def _create_trend_analysis_chart(self, business_type: str, location: str) -> str:
        """Create trend analysis visualization"""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Sample trend data
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        interest = [65, 72, 80, 75, 85, 90]  # Would come from trends data
        
        ax.plot(months, interest, marker='o', linewidth=2)
        ax.set_title(f'Consumer Interest Trends: {business_type} in {location}')
        ax.set_ylabel('Interest Score')
        ax.grid(True, alpha=0.3)
        
        filename = os.path.join(self.output_dir, f'trend_analysis_{business_type}_{location}.png')
        plt.savefig(filename)
        plt.close()
        
        return filename
    
    def _create_competitive_landscape(self, business_type: str, location: str) -> str:
        """Create competitive landscape visualization"""
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Sample competitor data
        competitors = ['Competitor A', 'Competitor B', 'Competitor C', 'Competitor D']
        ratings = [4.2, 3.8, 4.5, 3.9]
        reviews = [1200, 800, 1500, 600]
        
        scatter = ax.scatter(ratings, reviews, s=100, alpha=0.6)
        for i, competitor in enumerate(competitors):
            ax.annotate(competitor, (ratings[i], reviews[i]), xytext=(5, 5), 
                       textcoords='offset points')
        
        ax.set_xlabel('Average Rating')
        ax.set_ylabel('Number of Reviews')
        ax.set_title(f'Competitive Landscape: {business_type} in {location}')
        ax.grid(True, alpha=0.3)
        
        filename = os.path.join(self.output_dir, f'competitive_landscape_{business_type}_{location}.png')
        plt.savefig(filename)
        plt.close()
        
        return filename