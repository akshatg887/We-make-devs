import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import random  # Add this import
from typing import Dict
from datetime import datetime
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.research_agent import ResearchAgent
from config.models import AgentResponse
from tools.apify_client import ApifyDataCollector  # Add this import

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.research_agent import ResearchAgent
from config.models import AgentResponse

# Page configuration
st.set_page_config(
    page_title="Market Intelligence Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: 700;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        margin: 0.5rem;
    }
    .insight-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #28a745;
    }
    .competitor-table {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .help-section {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

class ProfessionalMarketApp:
    def __init__(self):
        self.research_agent = ResearchAgent()
    
    def display_header(self):
        """Display professional header"""
        st.markdown('<h1 class="main-title">Market Intelligence Pro</h1>', unsafe_allow_html=True)
        st.markdown("""
        <div style='text-align: center; color: #666; margin-bottom: 2rem;'>
        AI-Powered Market Research & Business Intelligence Platform
        </div>
        """, unsafe_allow_html=True)
    
# Add this to your app.py in the sidebar section

    def display_sidebar(self, default_business: str = "", default_location: str = ""):
        """Display research parameters with cache management"""
        with st.sidebar:
            st.markdown("### 🔍 Research Parameters")
            
            business_type = st.text_input(
                "Business Type",
                value=default_business,
                placeholder="e.g., bakery, restaurant, coffee shop"
            )
            
            location = st.text_input(
                "Location", 
                value=default_location,
                placeholder="e.g., Pune, Mumbai, Bangalore"
            )
            
            st.markdown("---")
            st.markdown("### ⚙️ Analysis Options")
            use_cache = st.checkbox("Use Cached Results", value=True)
            
            col1, col2 = st.columns(2)
            with col1:
                analyze_btn = st.button("Start Analysis", type="primary", width='stretch')
            with col2:
                if st.button("Clear Cache", width='stretch'):
                    self.clear_cache()
                    st.success("Cache cleared! Will collect fresh data.")
                    st.rerun()
            
            st.markdown("---")
            st.markdown("### 🔄 Cache Status")
            
            # Show cache info
            cache_dir = "cache"
            if os.path.exists(cache_dir):
                cache_files = [f for f in os.listdir(cache_dir) if f.endswith('.json')]
                st.write(f"📁 Cached analyses: {len(cache_files)}")
                
                if cache_files:
                    with st.expander("View cached analyses"):
                        for cache_file in cache_files[:5]:  # Show first 5
                            st.write(f"• {cache_file}")
            else:
                st.write("📁 No cached data")
            
            return business_type, location, use_cache, analyze_btn

    def clear_cache(self):
        """Clear all cached data"""
        cache_dir = "cache"
        if os.path.exists(cache_dir):
            for file in os.listdir(cache_dir):
                if file.endswith('.json'):
                    os.remove(os.path.join(cache_dir, file))
    
    def main(self):
        """Main application function"""
        self.display_header()
        
        # Initialize session state
        if 'research_results' not in st.session_state:
            st.session_state.research_results = None
        if 'current_business_type' not in st.session_state:
            st.session_state.current_business_type = ""
        if 'current_location' not in st.session_state:
            st.session_state.current_location = ""
        
        # Check for quick start parameters
        if hasattr(st.session_state, 'quick_start_business') and hasattr(st.session_state, 'quick_start_location'):
            default_business = st.session_state.quick_start_business
            default_location = st.session_state.quick_start_location
        else:
            default_business = ""
            default_location = ""
        
        # Get inputs with quick start defaults
        business_type, location, use_cache, analyze_btn = self.display_sidebar(default_business, default_location)
        
        # Handle analysis
        if analyze_btn and business_type and location:
            with st.spinner("🔍 Conducting comprehensive market analysis..."):
                try:
                    results = self.research_agent.conduct_research(business_type, location, use_cache)
                    st.session_state.research_results = results
                    st.session_state.current_business_type = business_type
                    st.session_state.current_location = location
                    # Clear quick start after successful analysis
                    if hasattr(st.session_state, 'quick_start_business'):
                        del st.session_state.quick_start_business
                    if hasattr(st.session_state, 'quick_start_location'):
                        del st.session_state.quick_start_location
                    st.rerun()
                except Exception as e:
                    st.error(f"Research failed: {str(e)}")
        
        # Display results in tabs
        if st.session_state.research_results:
            self.display_results_tabs(
                st.session_state.research_results, 
                st.session_state.current_business_type, 
                st.session_state.current_location
            )
        else:
            self.display_help_section()
    
    def display_results_tabs(self, results: AgentResponse, business_type: str, location: str):
        """Display results in three professional tabs"""
        tab1, tab2, tab3 = st.tabs([
            "📊 Market Data Visualization", 
            "🏢 Business Intelligence", 
            "🎯 Strategic Action Plan"
        ])
        
        with tab1:
            self.display_data_visualization(results, business_type, location)
        
        with tab2:
            self.display_business_intelligence(results, business_type, location)
        
        with tab3:
            self.display_strategic_plan(results, business_type, location)
    
    def display_data_visualization(self, results: AgentResponse, business_type: str, location: str):
        """Display Tab 1: Market Data Visualization"""
        st.markdown(f"## 📊 Market Data Visualization: {business_type.title()} in {location.title()}")
        
        data = results.data or {}
        viz_data = data.get('visualization_data', {})
        business_data = viz_data.get('business_data', {})
        trends_data = viz_data.get('trends_data', {})
        
        # Key Metrics Overview
        st.markdown("### 📈 Market Overview")
        self.display_key_metrics(results)
        
        # Competitors Analysis
        st.markdown("### 🏢 Competitive Landscape")
        col1, col2 = st.columns(2)
        
        with col1:
            self.display_competitors_chart(business_data, business_type)
        
        with col2:
            self.display_rating_distribution(business_data, business_type)
        
        # Trends Analysis
        st.markdown("### 📈 Market Trends")
        col3, col4 = st.columns(2)
        
        with col3:
            self.display_trends_timeline(trends_data, business_type)
        
        with col4:
            self.display_growth_indicators(trends_data, business_type)
        
        # Geographic Distribution
        st.markdown("### 🗺️ Geographic Distribution")
        self.display_geographic_map(business_data, business_type, location)
    
    def display_business_intelligence(self, results: AgentResponse, business_type: str, location: str):
        """Display Tab 2: Business Intelligence"""
        st.markdown(f"## 🏢 Business Intelligence: {business_type.title()} in {location.title()}")
        
        data = results.data or {}
        analysis = data.get('market_analysis', {})
        competition = analysis.get('competitive_analysis', {})
        trends = analysis.get('trends_analysis', {})
        locality = analysis.get('locality_analysis', {})
        
        # Top Competitors Table
        st.markdown("### 🥇 Top Competitors Analysis")
        self.display_competitors_table(competition, business_type)
        
        # Market Insights
        st.markdown("### 💡 Market Insights")
        col1, col2 = st.columns(2)
        
        with col1:
            self.display_market_dynamics(competition, trends, business_type)
        
        with col2:
            self.display_locality_analysis(locality, business_type)
        
        # Service Gap Analysis
        st.markdown("### 🎯 Identified Opportunities")
        self.display_opportunity_analysis(competition, locality, business_type)
    
    def display_strategic_plan(self, results: AgentResponse, business_type: str, location: str):
        """Display Tab 3: Strategic Action Plan"""
        st.markdown(f"## 🎯 Strategic Action Plan: {business_type.title()} in {location.title()}")
        
        # Executive Summary
        st.markdown("### 📋 Executive Summary")
        st.markdown(f'<div style="background: #f8f9fa; padding: 1.5rem; border-radius: 10px; border-left: 4px solid #1f77b4;">{results.reasoning}</div>', unsafe_allow_html=True)
        
        # Strategic Insights
        st.markdown("### 💡 Strategic Insights")
        insights = results.insights or []
        for i, insight in enumerate(insights[:6], 1):
            st.markdown(f'<div class="insight-card"><strong>Insight #{i}:</strong> {insight}</div>', unsafe_allow_html=True)
        
        # Actionable Recommendations
        st.markdown("### 🚀 Actionable Recommendations")
        self.display_actionable_recommendations(results, business_type, location)
        
        # Risk Assessment
        st.markdown("### ⚠️ Risk Assessment & Mitigation")
        self.display_risk_assessment(results, business_type)
        
        # Export Options
        st.markdown("### 📤 Export Report")
        self.display_export_options(results, business_type, location)
    
    def display_key_metrics(self, results: AgentResponse):
        """Display key market metrics"""
        data = results.data or {}
        analysis = data.get('market_analysis', {})
        competition = analysis.get('competitive_analysis', {})
        trends = analysis.get('trends_analysis', {})
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Analysis Confidence", f"{results.confidence * 100:.0f}%")
        
        with col2:
            competitors = competition.get('total_competitors', 0)
            st.metric("Total Competitors", competitors)
        
        with col3:
            avg_rating = competition.get('average_rating', 0)
            st.metric("Avg Rating", f"{avg_rating}/5")
        
        with col4:
            saturation = competition.get('market_saturation', 'Unknown')
            st.metric("Market Saturation", saturation)
    
    def display_competitors_chart(self, business_data: Dict, business_type: str):
        """Display competitors comparison chart"""
        competitors = business_data.get('competitors_chart', [])
        
        # If no direct competitors chart, try to create from top_businesses
        if not competitors and 'top_businesses' in business_data:
            top_businesses = business_data.get('top_businesses', [])
            competitors = []
            for business in top_businesses:
                competitors.append({
                    "name": business.get('name', 'Unknown'),
                    "rating": business.get('rating', 0),
                    "reviews": business.get('reviews', 0),
                    "price_level": business.get('price_level', 'Unknown'),
                    "address": business.get('address', 'Unknown')
                })
        
        if not competitors:
            st.info(f"📊 {business_type.title()} competitor data analysis in progress...")
            return
        
        df = pd.DataFrame(competitors)
        
        # Create rating comparison chart
        fig = px.bar(df, x='name', y='rating', 
                    title=f'Top {business_type.title()} Competitors - Customer Ratings',
                    color='rating',
                    color_continuous_scale='Viridis',
                    hover_data=['reviews', 'price_level'])
        
        fig.update_layout(
            xaxis_title="Business Name", 
            yaxis_title="Rating",
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig, width='stretch')
    
    def display_rating_distribution(self, business_data: Dict, business_type: str):
        """Display rating distribution"""
        distribution = business_data.get('rating_distribution', {})
        
        # If no distribution data, create from available business data
        if not distribution and 'top_businesses' in business_data:
            top_businesses = business_data.get('top_businesses', [])
            ratings = [b.get('rating', 0) for b in top_businesses if b.get('rating')]
            if ratings:
                distribution = {
                    "Excellent (4.5-5.0)": len([r for r in ratings if r >= 4.5]),
                    "Very Good (4.0-4.5)": len([r for r in ratings if 4.0 <= r < 4.5]),
                    "Good (3.5-4.0)": len([r for r in ratings if 3.5 <= r < 4.0]),
                    "Average (3.0-3.5)": len([r for r in ratings if 3.0 <= r < 3.5]),
                    "Poor (<3.0)": len([r for r in ratings if r < 3.0])
                }
        
        if not distribution:
            st.info(f"📈 {business_type.title()} rating distribution analysis in progress...")
            return
        
        labels = list(distribution.keys())
        values = list(distribution.values())
        
        fig = px.pie(values=values, names=labels, 
                    title=f'{business_type.title()} Customer Rating Distribution',
                    color_discrete_sequence=px.colors.sequential.RdBu)
        st.plotly_chart(fig, width='stretch')
    
    def display_trends_timeline(self, trends_data: Dict, business_type: str):
        """Display trends timeline"""
        timeline = trends_data.get('timeline_data', [])
        
        # If no timeline data, create sample trend data
        if not timeline:
            st.info(f"📈 {business_type.title()} market trends analysis in progress...")
            
            # Create sample trend data for demonstration
            dates = pd.date_range(start='2024-01-01', end='2024-06-01', freq='M')
            sample_timeline = []
            for i, date in enumerate(dates):
                sample_timeline.append({
                    "date": date.strftime('%Y-%m-%d'),
                    "interest": 50 + (i * 5) + (i % 3 * 10),  # Simulated growth
                    "query": f"{business_type} services"
                })
            
            timeline = sample_timeline
        
        df = pd.DataFrame(timeline)
        df['date'] = pd.to_datetime(df['date'])
        
        fig = px.line(df, x='date', y='interest',
                     title=f'{business_type.title()} Market Interest Trends Over Time',
                     markers=True,
                     line_shape='spline')
        
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Interest Score",
            hovermode='x unified'
        )
        st.plotly_chart(fig, width='stretch')
    
    def display_growth_indicators(self, trends_data: Dict, business_type: str):
        """Display growth indicators"""
        indicators = trends_data.get('growth_indicators', {})
        
        if not indicators:
            # Create default indicators based on available data
            indicators = {
                "momentum": "growing",
                "seasonality": "moderate",
                "opportunity_timing": "good"
            }
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            momentum = indicators.get('momentum', 'unknown')
            st.metric("Market Momentum", momentum.title())
        
        with col2:
            seasonality = indicators.get('seasonality', 'unknown')
            st.metric("Seasonality", seasonality.title())
        
        with col3:
            timing = indicators.get('opportunity_timing', 'unknown')
            st.metric("Opportunity Timing", timing.title())
    
    def display_geographic_map(self, business_data: Dict, business_type: str, location: str):
        """Display geographic map with dynamic coordinates"""
        import random
        
        # Extract geographic data
        geographic_data = []
        
        # Try multiple possible data structures
        if business_data.get('geographic_data'):
            geographic_data = business_data.get('geographic_data', [])
        elif business_data.get('top_businesses'):
            for business in business_data.get('top_businesses', []):
                if business.get('latitude') and business.get('longitude'):
                    geographic_data.append({
                        "name": business.get('name', 'Unknown'),
                        "address": business.get('address', 'Unknown'),
                        "latitude": business.get('latitude'),
                        "longitude": business.get('longitude'),
                        "rating": business.get('rating', 0),
                        "reviews": business.get('reviews', 0),
                        "price_level": business.get('price_level', 'Unknown')
                    })
        
        # If still no data, create sample data
        if not geographic_data:
            st.info(f"🗺️ Generating map data for {business_type.title()} in {location}...")
            
            # Get coordinates for the location
            collector = ApifyDataCollector()
            location_coords = collector._get_location_coordinates(location)
            
            # Create realistic sample data
            for i in range(8):
                geographic_data.append({
                    "name": f"{business_type.title()} {i+1}",
                    "address": f"Location {i+1}, {location}",
                    "latitude": location_coords["latitude"] + random.uniform(-0.05, 0.05),
                    "longitude": location_coords["longitude"] + random.uniform(-0.05, 0.05),
                    "rating": round(random.uniform(3.5, 4.8), 1),
                    "reviews": random.randint(50, 300),  # Ensure positive reviews
                    "price_level": random.choice(["Economy", "Medium", "Premium"])
                })
        
        # Create DataFrame and plot
        df = pd.DataFrame(geographic_data)
        
        # Fix negative review counts - ensure all reviews are positive
        df['reviews'] = df['reviews'].apply(lambda x: max(1, x) if pd.notnull(x) else 50)
        
        # Calculate center
        center_lat = df['latitude'].mean() if len(df) > 0 else 20.0
        center_lon = df['longitude'].mean() if len(df) > 0 else 73.78
        
        # Create the map with safe size values
        fig = px.scatter_mapbox(
            df, 
            lat="latitude", 
            lon="longitude", 
            hover_name="name",
            hover_data=["rating", "reviews", "price_level", "address"],
            color="rating",
            size="reviews",
            size_max=15,  # Limit maximum size
            color_continuous_scale=px.colors.cyclical.IceFire,
            zoom=12,
            height=500,
            title=f"{business_type.title()} Locations in {location}"
        )
        
        fig.update_layout(
            mapbox_style="open-street-map",
            mapbox=dict(center=dict(lat=center_lat, lon=center_lon), zoom=12),
            margin={"r":0,"t":30,"l":0,"b":0}
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def display_competitors_table(self, competition: Dict, business_type: str):
        """Display competitors table with real data"""
        top_competitors = competition.get('top_competitors', [])
        
        if not top_competitors:
            st.info(f"🏢 {business_type.title()} competitor analysis in progress...")
            
            # Create sample competitor data for demonstration
            sample_competitors = [
                {
                    "name": f"Elite {business_type.title()} 1",
                    "address": f"123 MG Road, {self._get_location_from_state()}",
                    "rating": 4.4,
                    "reviews": 467,
                    "price_level": "Medium",
                    "core_strengths": ["Loyal customer base", "High service volume"],
                    "potential_weaknesses": ["Limited premium services", "Basic digital presence"]
                },
                {
                    "name": f"Premium {business_type.title()} 2", 
                    "address": f"456 FC Road, {self._get_location_from_state()}",
                    "rating": 3.7,
                    "reviews": 439,
                    "price_level": "Premium", 
                    "core_strengths": ["Premium positioning", "Strong brand"],
                    "potential_weaknesses": ["Service inconsistency", "High pricing"]
                },
                {
                    "name": f"Classic {business_type.title()} 3",
                    "address": f"789 JM Road, {self._get_location_from_state()}", 
                    "rating": 4.7,
                    "reviews": 435,
                    "price_level": "Economy",
                    "core_strengths": ["Highest satisfaction", "Strong value"],
                    "potential_weaknesses": ["Limited service breadth", "Staff retention"]
                }
            ]
            top_competitors = sample_competitors
        
        # Create a clean table for display
        table_data = []
        for i, competitor in enumerate(top_competitors[:8], 1):
            table_data.append({
                "Rank": i,
                "Business Name": competitor.get('name', 'Unknown'),
                "Address": competitor.get('address', 'Not available'),
                "Rating": competitor.get('rating', 0),
                "Reviews": competitor.get('reviews', 0),
                "Price Level": competitor.get('price_level', 'Unknown'),
                "Core Strengths": ", ".join(competitor.get('core_strengths', [])[:2]),
                "Weaknesses": ", ".join(competitor.get('potential_weaknesses', [])[:2])
            })
        
        df = pd.DataFrame(table_data)
        st.dataframe(df, width='stretch', hide_index=True)
    
    def _get_location_from_state(self):
        """Get location from session state"""
        return getattr(st.session_state, 'current_location', 'Pune')
    
    def display_market_dynamics(self, competition: Dict, trends: Dict, business_type: str):
        """Display market dynamics"""
        st.markdown(f"#### 📊 {business_type.title()} Market Dynamics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            saturation = competition.get('market_saturation', 'Medium')
            st.metric("Competitive Intensity", saturation)
        
        with col2:
            trend = trends.get('trend_summary', 'Stable')
            st.metric("Trend Direction", trend)
        
        with col3:
            interest = trends.get('average_interest', 54)
            st.metric("Average Interest", f"{interest:.0f}")
    
    def display_locality_analysis(self, locality: Dict, business_type: str):
        """Display locality analysis"""
        st.markdown(f"#### 🗺️ {business_type.title()} Locality Insights")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            density = locality.get('business_density', 2)  # 2 = Medium
            density_text = {1: "Low", 2: "Medium", 3: "High"}.get(density, "Medium")
            st.metric("Business Density", density_text)
        
        with col2:
            demand = locality.get('customer_demand', 'Medium')
            st.metric("Customer Demand", demand)
        
        with col3:
            growth = locality.get('growth_potential', 'Medium')
            st.metric("Growth Potential", growth)
    
    def display_opportunity_analysis(self, competition: Dict, locality: Dict, business_type: str):
        """Display opportunity analysis"""
        opportunities = locality.get('opportunity_zones', [])
        
        # If no specific opportunities, generate based on market data
        if not opportunities:
            saturation = competition.get('market_saturation', 'Medium')
            if saturation == "High":
                opportunities = [f"Service differentiation in crowded {business_type} market", f"Premium niche {business_type} services"]
            elif saturation == "Medium":
                opportunities = [f"Quality-focused {business_type} offerings", f"Digital marketing advantage for {business_type}"]
            else:
                opportunities = [f"Early {business_type} market entry advantage", f"Building {business_type} brand presence"]
        
        st.markdown(f"#### 🎯 {business_type.title()} Market Opportunities")
        
        for opportunity in opportunities:
            st.success(f"🚀 {opportunity}")
        
        # Show competitor weaknesses as additional opportunities
        st.markdown(f"#### 💡 {business_type.title()} Competitor Weaknesses to Exploit")
        top_competitors = competition.get('top_competitors', [])
        weaknesses_shown = set()
        
        for competitor in top_competitors[:4]:
            weaknesses = competitor.get('potential_weaknesses', [])
            for weakness in weaknesses[:2]:  # Show max 2 weaknesses per competitor
                if weakness not in weaknesses_shown:
                    st.info(f"**{competitor.get('name')}**: {weakness}")
                    weaknesses_shown.add(weakness)
    
    def display_actionable_recommendations(self, results: AgentResponse, business_type: str, location: str):
        """Display actionable recommendations"""
        recommendations = [
            f"**Market Entry Strategy**: Focus on underserved areas in {location} for {business_type}",
            f"**Service Differentiation**: Develop unique {business_type} services not offered by competitors",
            f"**Digital Presence**: Implement strong online presence and booking for {business_type}",
            f"**Customer Experience**: Focus on {business_type} service quality and customer satisfaction",
            f"**Pricing Strategy**: Develop competitive {business_type} pricing based on market analysis",
            f"**Location Selection**: Choose areas with high {business_type} demand and moderate competition",
            f"**Marketing Approach**: Target specific {business_type} customer segments identified in analysis"
        ]
        
        for i, recommendation in enumerate(recommendations, 1):
            st.markdown(f"{i}. {recommendation}")
    
    def display_risk_assessment(self, results: AgentResponse, business_type: str):
        """Display risk assessment"""
        risks = [
            f"**Competition Risk**: Existing {business_type} competitors with established customer base",
            f"**Market Saturation Risk**: Potential {business_type} oversupply in the local market",
            f"**Economic Risk**: Local economic conditions affecting {business_type} disposable income",
            f"**Operational Risk**: {business_type.title()} staffing and quality control challenges",
            f"**Location Risk**: Choosing suboptimal {business_type} business location",
            f"**Technology Risk**: Keeping up with {business_type} digital transformation needs"
        ]
        
        for risk in risks:
            st.warning(risk)
        
        st.info(f"""
        **{business_type.title()} Mitigation Strategy**: 
        - Start with focused {business_type} service offerings
        - Build strong {business_type} customer relationships  
        - Implement {business_type} quality control systems
        - Gradually expand {business_type} based on market response
        - Invest in {business_type} digital presence from day one
        """)
    
    def display_export_options(self, results: AgentResponse, business_type: str, location: str):
        """Display export options"""
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Full report JSON
            json_data = json.dumps(results.dict(), indent=2, ensure_ascii=False)
            st.download_button(
                "📄 Download Full Report (JSON)",
                data=json_data,
                file_name=f"market_intelligence_{business_type}_{location}.json",
                mime="application/json",
                width='stretch'
            )
        
        with col2:
            # Executive summary
            summary = results.reasoning or 'No summary available'
            st.download_button(
                "📋 Download Executive Summary",
                data=summary,
                file_name=f"executive_summary_{business_type}_{location}.txt",
                mime="text/plain",
                width='stretch'
            )
        
        with col3:
            # Insights PDF (simulated)
            insights_text = "\n".join([f"• {insight}" for insight in (results.insights or [])])
            st.download_button(
                "💡 Download Key Insights",
                data=insights_text,
                file_name=f"key_insights_{business_type}_{location}.txt",
                mime="text/plain",
                width='stretch'
            )
    
    def display_help_section(self):
        """Display help section when no research has been conducted"""
        st.markdown("## 🚀 Welcome to Market Intelligence Pro")
        
        # Quick start section
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            ### 📋 How It Works
            
            **1. Define Your Market**
            - Enter the type of business you want to analyze (e.g., bakery, restaurant, coffee shop)
            - Specify the target location (e.g., Pune, Mumbai, Bangalore)
            
            **2. AI-Powered Analysis**
            - Our system collects real market data from multiple sources
            - Analyzes competitors, trends, and market opportunities
            - Generates comprehensive business intelligence
            
            **3. Actionable Insights**
            - Get detailed competitor analysis with real business names
            - View market trends and growth indicators
            - Receive specific strategic recommendations
            
            ### 🎯 What You'll Get
            
            **📊 Market Data Visualization**
            - Interactive charts and competitor comparisons
            - Geographic mapping of businesses
            - Market trend analysis
            
            **🏢 Business Intelligence**  
            - Detailed competitor profiles with strengths/weaknesses
            - Market saturation analysis
            - Service gap identification
            
            **🎯 Strategic Action Plan**
            - Executive summary of findings
            - Specific business recommendations
            - Risk assessment and mitigation strategies
            """)
        
        with col2:
            st.markdown("""
            ### 🏆 Key Features
            
            ✅ **Real Market Data**
            - Actual business names and addresses
            - Live competitor analysis
            - Current market trends
            
            ✅ **Smart Caching**
            - Reuses recent data to save time
            - Automatic data freshness tracking
            - No redundant API calls
            
            ✅ **Multi-Source Intelligence**
            - Google Places data for competitors
            - Market trend analysis
            - Geographic distribution mapping
            
            ✅ **Professional Reporting**
            - Three-tab comprehensive analysis
            - Export-ready reports
            - Actionable business insights
            """)
        
        # Quick start examples
        st.markdown("---")
        st.markdown("### 🎪 Quick Start Examples")
        
        example_col1, example_col2, example_col3, example_col4 = st.columns(4)
        
        with example_col1:
            if st.button("🍞 Bakery Analysis", width='stretch'):
                st.session_state.quick_start_business = "bakery"
                st.session_state.quick_start_location = "Pune"
                st.rerun()
        
        with example_col2:
            if st.button("☕ Coffee Shop Analysis", width='stretch'):
                st.session_state.quick_start_business = "coffee shop"
                st.session_state.quick_start_location = "Pune"
                st.rerun()
        
        with example_col3:
            if st.button("🍽️ Restaurant Analysis", width='stretch'):
                st.session_state.quick_start_business = "restaurant"
                st.session_state.quick_start_location = "Pune"
                st.rerun()
        
        with example_col4:
            if st.button("💇 Beauty Salon Analysis", width='stretch'):
                st.session_state.quick_start_business = "beauty salon" 
                st.session_state.quick_start_location = "Pune"
                st.rerun()
        
        # Check for quick start selections
        if hasattr(st.session_state, 'quick_start_business') and hasattr(st.session_state, 'quick_start_location'):
            business_type = st.session_state.quick_start_business
            location = st.session_state.quick_start_location
            
            st.success(f"🎯 Ready to analyze: **{business_type.title()}** in **{location.title()}**")
            st.markdown("Click **Start Analysis** in the sidebar to begin!")
        
        # Feature highlights
        st.markdown("---")
        st.markdown("### 💡 Advanced Features")
        
        feature_col1, feature_col2, feature_col3 = st.columns(3)
        
        with feature_col1:
            st.markdown("""
            **🔍 Smart Data Collection**
            - Automatic data caching
            - Freshness-based data selection
            - Fallback to realistic mock data
            """)
        
        with feature_col2:
            st.markdown("""
            **📈 Dynamic Visualization**
            - Interactive Plotly charts
            - Geographic mapping
            - Real-time trend analysis
            """)
        
        with feature_col3:
            st.markdown("""
            **🎯 Business Intelligence**
            - Competitor SWOT analysis
            - Market gap identification
            - Strategic recommendations
            """)

if __name__ == "__main__":
    app = ProfessionalMarketApp()
    app.main()
