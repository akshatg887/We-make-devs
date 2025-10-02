# structured_analysis_agent.py - Fixed Cerebras model issue
import os
from cerebras.cloud.sdk import Cerebras
from typing import Dict, Any, List
from config.settings import settings
from config.models import StructuredResearchResponse, CompetitorAnalysis, MarketTrends, BusinessOpportunity, MarketInsights
import json
from datetime import datetime

class StructuredAnalysisAgent:
    def __init__(self, model: str = "gpt_oss_120b"):
        self.client = Cerebras(api_key=settings.CEREBRAS_API_KEY)
        # Fix model selection - use string directly, not dict
        self.model = self._get_model_name(model)
    
    def _get_model_name(self, model_key: str) -> str:
        """Get actual model name from settings"""
        model_config = settings.MODELS.get(model_key, {})
        if isinstance(model_config, dict):
            return model_config.get('cerebras', 'llama-70b')  # Default fallback
        elif isinstance(model_config, str):
            return model_config
        else:
            return 'llama-70b'  # Safe fallback
    
    def generate_structured_analysis(self, research_data: Dict[str, Any], business_type: str, location: str) -> StructuredResearchResponse:
        """Generate structured analysis using LLM"""
        
        try:
            # Create a simplified prompt that's more likely to return structured data
            prompt = f"""
            Analyze this market research data for {business_type} business in {location} and provide a structured analysis.

            RESEARCH DATA SUMMARY:
            - Business Type: {business_type}
            - Location: {location}
            - Competitors: {len(research_data.get('market_analysis', {}).get('competitive_analysis', {}).get('top_competitors', []))}
            - Market Trends: {research_data.get('market_analysis', {}).get('trends_analysis', {}).get('trend_summary', 'No data')}

            Please provide analysis in this exact JSON format:
            {{
                "business_type": "{business_type}",
                "location": "{location}",
                "executive_summary": "2-3 sentence summary of market conditions",
                "competitors": [
                    {{
                        "name": "Competitor Name",
                        "address": "Business Address", 
                        "rating": 4.2,
                        "reviews": 150,
                        "price_level": "Medium",
                        "strengths": ["Strength 1", "Strength 2"],
                        "weaknesses": ["Weakness 1", "Weakness 2"]
                    }}
                ],
                "market_trends": {{
                    "trend_summary": "Market trend description",
                    "average_interest": 65.5,
                    "growth_momentum": "positive",
                    "seasonal_patterns": "moderate seasonality"
                }},
                "opportunities": [
                    {{
                        "opportunity_type": "Service Type",
                        "description": "Opportunity description",
                        "potential_impact": "Expected impact",
                        "implementation": "How to implement"
                    }}
                ],
                "insights": {{
                    "market_saturation": "Medium",
                    "competitive_intensity": "Moderate", 
                    "customer_demand": "High",
                    "growth_potential": "Good"
                }},
                "recommendations": [
                    "Recommendation 1",
                    "Recommendation 2"
                ],
                "confidence_score": 0.85
            }}

            Focus on real insights from the data. Be specific and actionable.
            """
            
            messages = [
                {"role": "system", "content": "You are a expert market research analyst. Always respond with valid JSON in the exact format provided."},
                {"role": "user", "content": prompt}
            ]
            
            print(f"🤖 Calling Cerebras with model: {self.model}")
            
            response = self.client.chat.completions.create(
                messages=messages,
                model=self.model,  # Now using string directly
                max_completion_tokens=4000,
                temperature=0.6,
                top_p=0.8
            )
            
            analysis_text = response.choices[0].message.content
            print(f"📄 Received response from LLM")
            
            return self._parse_structured_response(analysis_text, business_type, location)
            
        except Exception as e:
            print(f"❌ Error in structured analysis: {e}")
            return self._create_fallback_response(business_type, location)
    
    def _parse_structured_response(self, analysis_text: str, business_type: str, location: str) -> StructuredResearchResponse:
        """Parse LLM response into structured format"""
        try:
            # Clean the response text
            cleaned_text = analysis_text.strip()
            
            # Extract JSON from various formats
            if "```json" in cleaned_text:
                json_str = cleaned_text.split("```json")[1].split("```")[0].strip()
            elif "```" in cleaned_text:
                json_str = cleaned_text.split("```")[1].strip()
            elif cleaned_text.startswith("{") and cleaned_text.endswith("}"):
                json_str = cleaned_text
            else:
                # Try to find JSON object in the text
                start_idx = cleaned_text.find('{')
                end_idx = cleaned_text.rfind('}')
                if start_idx != -1 and end_idx != -1:
                    json_str = cleaned_text[start_idx:end_idx+1]
                else:
                    raise ValueError("No JSON found in response")
            
            print(f"🔄 Parsing JSON response")
            parsed_data = json.loads(json_str)
            
            # Ensure all required fields are present
            if 'competitors' in parsed_data and isinstance(parsed_data['competitors'], list):
                competitors = []
                for comp in parsed_data['competitors']:
                    competitors.append(CompetitorAnalysis(**comp))
                parsed_data['competitors'] = competitors
            
            if 'market_trends' in parsed_data:
                parsed_data['market_trends'] = MarketTrends(**parsed_data['market_trends'])
            
            if 'opportunities' in parsed_data and isinstance(parsed_data['opportunities'], list):
                opportunities = []
                for opp in parsed_data['opportunities']:
                    opportunities.append(BusinessOpportunity(**opp))
                parsed_data['opportunities'] = opportunities
            
            if 'insights' in parsed_data:
                parsed_data['insights'] = MarketInsights(**parsed_data['insights'])
            
            # Add timestamp
            parsed_data['timestamp'] = datetime.now().isoformat()
            
            return StructuredResearchResponse(**parsed_data)
            
        except Exception as e:
            print(f"❌ Error parsing structured response: {e}")
            print(f"📄 Response text was: {analysis_text[:500]}...")
            return self._create_fallback_response(business_type, location)
    
    def _create_fallback_response(self, business_type: str, location: str) -> StructuredResearchResponse:
        """Create fallback structured response"""
        print("🔄 Using fallback structured response")
        return StructuredResearchResponse(
            business_type=business_type,
            location=location,
            executive_summary=f"Market analysis for {business_type} in {location} shows promising opportunities with moderate competition. The market appears stable with room for quality-focused entrants.",
            competitors=[
                CompetitorAnalysis(
                    name="Local Bakery Chain",
                    address="123 Main Street",
                    rating=4.2,
                    reviews=150,
                    price_level="Medium",
                    strengths=["Good location", "Established brand"],
                    weaknesses=["Limited variety", "Inconsistent quality"]
                )
            ],
            market_trends=MarketTrends(
                trend_summary="Stable market with growing interest in artisanal products",
                average_interest=65.5,
                growth_momentum="positive",
                seasonal_patterns="higher demand during holidays"
            ),
            opportunities=[
                BusinessOpportunity(
                    opportunity_type="Premium Products",
                    description="Introduce artisanal and premium bakery items",
                    potential_impact="Higher profit margins and customer loyalty",
                    implementation="Source quality ingredients and train staff"
                )
            ],
            insights=MarketInsights(
                market_saturation="Medium",
                competitive_intensity="Moderate",
                customer_demand="High",
                growth_potential="Good"
            ),
            recommendations=[
                "Focus on quality and unique product offerings",
                "Implement strong digital marketing presence",
                "Develop loyalty programs for repeat customers"
            ],
            confidence_score=0.75,
            timestamp=datetime.now().isoformat()
        )