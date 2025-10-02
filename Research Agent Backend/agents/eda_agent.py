# eda_agent.py - Updated for better insights generation

import os
from cerebras.cloud.sdk import Cerebras
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple
import json
from config.settings import settings
from tools.data_processor import DataProcessor

class EDAAgent:
    def __init__(self, model: str = "llama_70b"):
        self.client = Cerebras(api_key=settings.CEREBRAS_API_KEY)
        self.model = settings.MODELS[model]
        self.data_processor = DataProcessor()
    
    def perform_comprehensive_eda(self, raw_data: Dict, business_type: str, location: str) -> Tuple[Dict, List[str]]:
        """Perform comprehensive EDA and generate insights"""
        
        print(f"🔍 Performing comprehensive EDA for {business_type} in {location}...")
        
        # Step 1: Data sampling and statistical analysis
        sampled_data, statistics = self._sample_and_analyze_data(raw_data)
        
        # Step 2: Generate EDA insights using LLM with improved prompt
        eda_insights = self._generate_eda_insights(sampled_data, statistics, business_type, location)
        
        # Step 3: Extract key patterns and trends
        key_patterns = self._extract_key_patterns(eda_insights, statistics)
        
        # Step 4: Generate actionable business insights
        business_insights = self._generate_business_insights(key_patterns, business_type, location)
        
        return {
            "sampled_data": sampled_data,
            "statistics": statistics,
            "eda_insights": eda_insights,
            "key_patterns": key_patterns,
            "location": location,
            "business_type": business_type
        }, business_insights
    
    def _generate_eda_insights(self, sampled_data: Dict, statistics: Dict, business_type: str, location: str) -> List[str]:
        """Generate EDA insights using LLM with improved prompt"""
        
        prompt = f"""
        As a senior data analyst, perform comprehensive Exploratory Data Analysis (EDA) on market research data for {business_type} businesses in {location}.

        DATA CONTEXT:
        - Business Type: {business_type}
        - Location: {location}
        - Data Collection: Recent market data from Google Places and Trends API

        SAMPLED BUSINESS DATA:
        {json.dumps(sampled_data.get('places', [])[:10], indent=2)}

        COMPREHENSIVE STATISTICS:
        {json.dumps(statistics, indent=2)}

        Analyze this data thoroughly and provide 7-10 actionable EDA insights focusing on:

        1. DATA QUALITY ASSESSMENT:
           - Missing values and data completeness
           - Data reliability and potential biases
           - Sample size adequacy

        2. MARKET STRUCTURE ANALYSIS:
           - Competitive landscape density
           - Market concentration indicators
           - Geographic distribution patterns

        3. CUSTOMER BEHAVIOR PATTERNS:
           - Rating distribution and customer satisfaction
           - Review volume patterns
           - Price sensitivity indicators

        4. BUSINESS PERFORMANCE METRICS:
           - Performance gaps in the market
           - Service quality variations
           - Market leader characteristics

        5. TREND ANALYSIS:
           - Search interest patterns
           - Seasonal variations
           - Growth momentum

        Format each insight as:
        "INSIGHT: [Clear finding] - IMPLICATION: [What this means for business] - DATA: [Supporting metric]"

        Make insights specific to {business_type} in {location} and actionable for business strategy.
        """
        
        response = self._call_llm(prompt)
        return self._parse_enhanced_insights(response)
    
    def _parse_enhanced_insights(self, text: str) -> List[str]:
        """Parse LLM response into structured insights with better formatting"""
        insights = []
        lines = text.split('\n')
        
        current_insight = ""
        for line in lines:
            line = line.strip()
            if line.startswith('INSIGHT:') or line.startswith('•') or line.startswith('-') or (line and line[0].isdigit() and '.' in line[:3]):
                if current_insight:
                    insights.append(current_insight.strip())
                    current_insight = ""
                
                # Clean the line
                clean_line = line.replace('INSIGHT:', '').replace('•', '').replace('-', '').strip()
                if clean_line and len(clean_line) > 20:
                    current_insight = clean_line
            elif current_insight and line and not line.startswith('IMPLEMENTATION:') and not line.startswith('DATA:'):
                current_insight += " " + line
        
        if current_insight:
            insights.append(current_insight.strip())
        
        # Fallback: split by sentences if no structured insights found
        if not insights or len(insights) < 3:
            sentences = [s.strip() + '.' for s in text.split('.') if len(s.strip()) > 30]
            insights = sentences[:7]
        
        return insights[:10]
    
    def _generate_business_insights(self, key_patterns: Dict, business_type: str, location: str) -> List[str]:
        """Generate actionable business insights from patterns"""
        
        prompt = f"""
        As a business strategy expert, generate actionable insights for opening a {business_type} in {location}.

        MARKET ANALYSIS PATTERNS:
        {json.dumps(key_patterns, indent=2)}

        Generate 5-7 strategic business insights focusing on:

        1. MARKET ENTRY STRATEGY:
           - Optimal timing and positioning
           - Competitive differentiation
           - Target customer segments

        2. OPERATIONAL EXCELLENCE:
           - Service quality benchmarks
           - Pricing strategy recommendations
           - Customer experience standards

        3. GROWTH OPPORTUNITIES:
           - Underserved market segments
           - Geographic opportunities
           - Service expansion possibilities

        4. RISK MITIGATION:
           - Competitive threats
           - Market saturation risks
           - Customer acquisition challenges

        Format each insight as:
        "STRATEGY: [Specific action] - IMPACT: [Expected outcome] - EXECUTION: [How to implement]"

        Make insights specific, measurable, and directly applicable to {business_type} in {location}.
        """
        
        response = self._call_llm(prompt)
        return self._parse_enhanced_insights(response)

    
    def _parse_insights(self, text: str) -> List[str]:
        """Parse LLM response into structured insights"""
        insights = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if line and any(line.startswith(str(i)) for i in range(1, 10)):
                # Remove numbering and clean
                insight = line[2:].strip() if len(line) > 2 and line[1] in ['.', ')'] else line
                if insight and len(insight) > 20:
                    insights.append(insight)
        
        # Fallback: split by sentences
        if not insights:
            sentences = [s.strip() + '.' for s in text.split('.') if len(s.strip()) > 30]
            insights = sentences[:7]
        
        return insights[:7]
    
    def _call_llm(self, prompt: str) -> str:
        """Make LLM call to Cerebras"""
        try:
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model,
                max_completion_tokens=3000,
                temperature=0.6,
                top_p=0.8
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error in EDA LLM call: {str(e)}"