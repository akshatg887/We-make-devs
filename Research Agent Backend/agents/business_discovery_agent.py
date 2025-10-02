# business_discovery_agent.py
import os
from cerebras.cloud.sdk import Cerebras
from typing import Dict, Any, List
from config.settings import settings
from config.models import BusinessSuggestion, CityBusinessReport, ComprehensiveBusinessAnalysis
from tools.apify_client import ApifyDataCollector
import json
from datetime import datetime

class BusinessDiscoveryAgent:
    def __init__(self, model: str = "gpt_oss_120b"):
        self.client = Cerebras(api_key=settings.CEREBRAS_API_KEY)
        self.model = self._get_model_name(model)
        self.apify_client = ApifyDataCollector()
    
    def _get_model_name(self, model_key: str) -> str:
        """Get actual model name from settings"""
        model_config = settings.MODELS.get(model_key, {})
        if isinstance(model_config, dict):
            return model_config.get('cerebras', 'llama-70b')
        elif isinstance(model_config, str):
            return model_config
        else:
            return 'llama-70b'
    
    def discover_business_opportunities(self, city: str) -> CityBusinessReport:
        """Discover and suggest business opportunities for a city"""
        print(f"🔍 Discovering business opportunities for {city}...")
        
        try:
            # Collect initial city data
            city_data = self._collect_city_data(city)
            
            prompt = f"""
            As a business opportunity analyst, analyze {city} and suggest the most viable business opportunities.
            
            CITY CONTEXT:
            - City: {city}
            - Population Tier: {city_data.get('population_tier', 'Medium')}
            - Economic Indicators: {city_data.get('economic_indicators', {})}
            
            Suggest 5-7 business opportunities with this exact JSON structure:
            {{
                "city": "{city}",
                "population_tier": "Medium/Large/Metro",
                "economic_indicators": {{
                    "consumer_spending": "High/Medium/Low",
                    "commercial_activity": "High/Medium/Low", 
                    "growth_trajectory": "Rapid/Moderate/Slow"
                }},
                "top_business_suggestions": [
                    {{
                        "business_type": "e.g., Specialty Coffee Shop",
                        "viability_score": 85.5,
                        "investment_range": "₹15-25 lakhs",
                        "competition_level": "Medium",
                        "growth_potential": "High",
                        "key_opportunities": ["Growing youth population", "Digital adoption"],
                        "challenges": ["Real estate costs", "Staff availability"]
                    }}
                ],
                "market_trends": [
                    "Trend 1",
                    "Trend 2" 
                ],
                "consumer_behavior": {{
                    "spending_patterns": "Description",
                    "preferred_categories": ["Category1", "Category2"],
                    "digital_adoption": "High/Medium/Low"
                }}
            }}
            
            Focus on:
            - Current market gaps in {city}
            - Emerging consumer trends
            - Sustainable business models
            - Digital integration opportunities
            - Local economic factors
            """
            
            messages = [
                {"role": "system", "content": "You are an expert business opportunity analyst. Provide data-driven, realistic business suggestions."},
                {"role": "user", "content": prompt}
            ]
            
            response = self.client.chat.completions.create(
                messages=messages,
                model=self.model,
                max_completion_tokens=4000,
                temperature=0.7,
                top_p=0.8
            )
            
            analysis_text = response.choices[0].message.content
            return self._parse_city_report(analysis_text, city)
            
        except Exception as e:
            print(f"❌ Business discovery failed: {e}")
            return self._create_fallback_city_report(city)
    
    def generate_comprehensive_analysis(self, business_type: str, city: str) -> ComprehensiveBusinessAnalysis:
        """Generate comprehensive business analysis with real-time data"""
        print(f"📊 Generating comprehensive analysis for {business_type} in {city}...")
        
        try:
            # Collect real-time data
            real_time_data = self._collect_real_time_data(business_type, city)
            
            prompt = f"""
            Create a comprehensive business analysis for {business_type} in {city}.
            
            REAL-TIME MARKET DATA:
            {json.dumps(real_time_data, indent=2)}
            
            Provide analysis in this exact JSON format:
            {{
                "business_type": "{business_type}",
                "location": "{city}",
                "executive_summary": "2-3 paragraph comprehensive summary",
                "market_overview": {{
                    "market_size": "Estimate",
                    "growth_rate": "X% annually", 
                    "customer_segments": ["Segment1", "Segment2"],
                    "key_drivers": ["Driver1", "Driver2"]
                }},
                "operational_requirements": {{
                    "space_needed": "XXX sq ft",
                    "staff_requirements": "X-Y people",
                    "equipment_needs": ["Item1", "Item2"],
                    "licenses_required": ["License1", "License2"]
                }},
                "financial_projections": {{
                    "initial_investment": "₹X-Y lakhs",
                    "monthly_operating_costs": "₹X lakhs",
                    "break_even_period": "X-Y months",
                    "projected_roi": "X% annually"
                }},
                "competitor_analysis": {{
                    "total_competitors": X,
                    "competitive_landscape": "Description",
                    "competitor_strengths": ["Strength1", "Strength2"],
                    "competitor_weaknesses": ["Weakness1", "Weakness2"],
                    "market_gaps": ["Gap1", "Gap2"]
                }},
                "risk_assessment": {{
                    "market_risks": ["Risk1", "Risk2"],
                    "operational_risks": ["Risk1", "Risk2"], 
                    "financial_risks": ["Risk1", "Risk2"],
                    "mitigation_strategies": ["Strategy1", "Strategy2"]
                }},
                "strategic_recommendations": [
                    "Recommendation 1",
                    "Recommendation 2",
                    "Recommendation 3"
                ],
                "confidence_score": 0.85
            }}
            
            Be specific, data-driven, and focus on actionable insights.
            """
            
            messages = [
                {"role": "system", "content": "You are a comprehensive business analyst. Provide detailed, practical business analysis."},
                {"role": "user", "content": prompt}
            ]
            
            response = self.client.chat.completions.create(
                messages=messages,
                model=self.model,
                max_completion_tokens=5000,
                temperature=0.6,
                top_p=0.8
            )
            
            analysis_text = response.choices[0].message.content
            return self._parse_comprehensive_analysis(analysis_text, business_type, city, real_time_data)
            
        except Exception as e:
            print(f"❌ Comprehensive analysis failed: {e}")
            return self._create_fallback_comprehensive_analysis(business_type, city)
    
    def _collect_city_data(self, city: str) -> Dict[str, Any]:
        """Collect basic city data for analysis"""
        # This would integrate with geographic/economic APIs in production
        city_tiers = {
            'mumbai': 'Metro', 'delhi': 'Metro', 'bangalore': 'Metro', 
            'chennai': 'Metro', 'kolkata': 'Metro', 'hyderabad': 'Metro',
            'pune': 'Large', 'ahmedabad': 'Large', 'jaipur': 'Medium'
        }
        
        return {
            'population_tier': city_tiers.get(city.lower(), 'Medium'),
            'economic_indicators': {
                'consumer_spending': 'High' if city.lower() in ['mumbai', 'delhi', 'bangalore'] else 'Medium',
                'commercial_activity': 'High',
                'growth_trajectory': 'Rapid' if city.lower() in ['bangalore', 'pune', 'hyderabad'] else 'Moderate'
            }
        }
    
    def _collect_real_time_data(self, business_type: str, city: str) -> Dict[str, Any]:
        """Collect real-time market data using Apify"""
        print(f"🌐 Collecting real-time data for {business_type} in {city}...")
        
        try:
            # Use Apify client to get fresh data
            search_queries = [
                f"{business_type} in {city}",
                f"best {business_type} {city}",
                f"{business_type} services {city}"
            ]
            
            places_data = self.apify_client.scrape_places_data(search_queries, city)
            trends_data = self.apify_client.scrape_trends_data([business_type], city)
            
            return {
                'places_data_summary': {
                    'total_businesses': len(places_data),
                    'avg_rating': self._calculate_avg_rating(places_data),
                    'price_levels': self._analyze_price_levels(places_data),
                    'top_competitors': places_data[:5] if places_data else []
                },
                'trends_data_summary': {
                    'total_trend_points': len(trends_data),
                    'interest_trend': self._analyze_trend_direction(trends_data),
                    'peak_interest': max([t.get('value', 0) for t in trends_data]) if trends_data else 0
                },
                'data_freshness': 'real_time',
                'collection_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"⚠️ Real-time data collection failed: {e}")
            return {
                'places_data_summary': {'total_businesses': 0, 'avg_rating': 0, 'price_levels': {}, 'top_competitors': []},
                'trends_data_summary': {'total_trend_points': 0, 'interest_trend': 'unknown', 'peak_interest': 0},
                'data_freshness': 'fallback',
                'collection_time': datetime.now().isoformat()
            }
    
    def _calculate_avg_rating(self, places_data: List[Dict]) -> float:
        """Calculate average rating from places data"""
        ratings = [p.get('rating', 0) for p in places_data if p.get('rating')]
        return round(sum(ratings) / len(ratings), 2) if ratings else 0
    
    def _analyze_price_levels(self, places_data: List[Dict]) -> Dict[str, int]:
        """Analyze price level distribution"""
        price_levels = [p.get('priceLevel', 0) for p in places_data if p.get('priceLevel')]
        return {
            'budget': len([p for p in price_levels if p == 1]),
            'medium': len([p for p in price_levels if p == 2]),
            'premium': len([p for p in price_levels if p in [3, 4]])
        }
    
    def _analyze_trend_direction(self, trends_data: List[Dict]) -> str:
        """Analyze trend direction from trends data"""
        if not trends_data or len(trends_data) < 2:
            return 'stable'
        
        values = [t.get('value', 0) for t in trends_data]
        if values[-1] > values[0] + 10:
            return 'growing'
        elif values[-1] < values[0] - 10:
            return 'declining'
        else:
            return 'stable'
    
    def _parse_city_report(self, analysis_text: str, city: str) -> CityBusinessReport:
        """Parse city business report from LLM response"""
        try:
            if "```json" in analysis_text:
                json_str = analysis_text.split("```json")[1].split("```")[0].strip()
            elif analysis_text.startswith("{") and analysis_text.endswith("}"):
                json_str = analysis_text
            else:
                raise ValueError("No valid JSON found")
            
            parsed_data = json.loads(json_str)
            parsed_data['timestamp'] = datetime.now().isoformat()
            
            # Convert business suggestions to proper objects
            if 'top_business_suggestions' in parsed_data:
                suggestions = []
                for suggestion in parsed_data['top_business_suggestions']:
                    suggestions.append(BusinessSuggestion(**suggestion))
                parsed_data['top_business_suggestions'] = suggestions
            
            return CityBusinessReport(**parsed_data)
            
        except Exception as e:
            print(f"❌ Error parsing city report: {e}")
            return self._create_fallback_city_report(city)
    
    def _parse_comprehensive_analysis(self, analysis_text: str, business_type: str, city: str, real_time_data: Dict) -> ComprehensiveBusinessAnalysis:
        """Parse comprehensive analysis from LLM response"""
        try:
            if "```json" in analysis_text:
                json_str = analysis_text.split("```json")[1].split("```")[0].strip()
            elif analysis_text.startswith("{") and analysis_text.endswith("}"):
                json_str = analysis_text
            else:
                raise ValueError("No valid JSON found")
            
            parsed_data = json.loads(json_str)
            parsed_data['timestamp'] = datetime.now().isoformat()
            parsed_data['real_time_data'] = real_time_data
            
            return ComprehensiveBusinessAnalysis(**parsed_data)
            
        except Exception as e:
            print(f"❌ Error parsing comprehensive analysis: {e}")
            return self._create_fallback_comprehensive_analysis(business_type, city)
    
    def _create_fallback_city_report(self, city: str) -> CityBusinessReport:
        """Create fallback city business report"""
        return CityBusinessReport(
            city=city,
            population_tier="Medium",
            economic_indicators={
                "consumer_spending": "Medium",
                "commercial_activity": "Medium",
                "growth_trajectory": "Moderate"
            },
            top_business_suggestions=[
                BusinessSuggestion(
                    business_type="Food & Beverage",
                    viability_score=75.0,
                    investment_range="₹20-40 lakhs",
                    competition_level="Medium",
                    growth_potential="High",
                    key_opportunities=["Growing urban population", "Rising disposable income"],
                    challenges=["High competition", "Real estate costs"]
                )
            ],
            market_trends=["Digital transformation", "Focus on sustainability"],
            consumer_behavior={
                "spending_patterns": "Value-conscious with quality focus",
                "preferred_categories": ["Food", "Retail", "Services"],
                "digital_adoption": "High"
            },
            timestamp=datetime.now().isoformat()
        )
    
    def _create_fallback_comprehensive_analysis(self, business_type: str, city: str) -> ComprehensiveBusinessAnalysis:
        """Create fallback comprehensive analysis"""
        return ComprehensiveBusinessAnalysis(
            business_type=business_type,
            location=city,
            executive_summary=f"Comprehensive analysis for {business_type} in {city}. Market shows moderate competition with good growth potential for quality-focused entrants.",
            market_overview={
                "market_size": "Growing",
                "growth_rate": "10-15% annually",
                "customer_segments": ["Urban professionals", "Families", "Youth"],
                "key_drivers": ["Urbanization", "Digital adoption", "Quality demand"]
            },
            operational_requirements={
                "space_needed": "500-1000 sq ft",
                "staff_requirements": "5-8 people",
                "equipment_needs": ["Basic infrastructure", "Digital systems"],
                "licenses_required": ["Business license", "GST registration"]
            },
            financial_projections={
                "initial_investment": "₹25-50 lakhs",
                "monthly_operating_costs": "₹2-4 lakhs",
                "break_even_period": "18-24 months",
                "projected_roi": "20-30% annually"
            },
            competitor_analysis={
                "total_competitors": 15,
                "competitive_landscape": "Moderately competitive",
                "competitor_strengths": ["Established brands", "Customer loyalty"],
                "competitor_weaknesses": ["Slow innovation", "Digital gap"],
                "market_gaps": ["Premium services", "Digital integration"]
            },
            risk_assessment={
                "market_risks": ["New competitors", "Economic slowdown"],
                "operational_risks": ["Staff turnover", "Supply chain"],
                "financial_risks": ["Cash flow management", "Initial losses"],
                "mitigation_strategies": ["Quality focus", "Digital marketing", "Cost control"]
            },
            strategic_recommendations=[
                "Focus on quality differentiation",
                "Implement strong digital presence",
                "Build customer loyalty programs"
            ],
            real_time_data={},
            confidence_score=0.7,
            timestamp=datetime.now().isoformat()
        )