# graphs/research_graph.py
from typing import Dict, Any, List, TypedDict
from pydantic import BaseModel, Field
import json
from datetime import datetime

from agents.research_agent import ResearchAgent
from agents.analysis_agent import AnalysisAgent
from agents.evaluation_agent import EvaluationAgent
from agents.eda_agent import EDAAgent
from tools.llm_client import MultiProviderLLM

# Structured output models using Pydantic
class BusinessSuggestion(BaseModel):
    business_niche: str = Field(description="Suggested business niche")
    reason: str = Field(description="Why this business is suitable")
    market_opportunity: str = Field(description="Market opportunity analysis")
    investment_range: str = Field(description="Estimated investment range")
    growth_potential: str = Field(description="Growth potential assessment")

class ScrapedDataSummary(BaseModel):
    total_businesses: int = Field(description="Total businesses found")
    average_rating: float = Field(description="Average rating in the market")
    market_saturation: str = Field(description="Market saturation level")
    top_competitors: List[str] = Field(description="List of top competitors")
    data_quality: str = Field(description="Quality of scraped data")

class BusinessInsights(BaseModel):
    key_insights: List[str] = Field(description="Key business insights")
    opportunities: List[str] = Field(description="Market opportunities")
    risks: List[str] = Field(description="Potential risks")
    recommendations: List[str] = Field(description="Strategic recommendations")

class DetailedBusinessReport(BaseModel):
    executive_summary: str = Field(description="Executive summary")
    market_analysis: str = Field(description="Detailed market analysis")
    competitive_landscape: str = Field(description="Competitive analysis")
    financial_projections: str = Field(description="Financial projections")
    implementation_plan: str = Field(description="Implementation plan")
    risk_assessment: str = Field(description="Risk assessment")

class MultiAgentResearchGraph:
    def __init__(self):
        self.research_agent = ResearchAgent()
        self.analysis_agent = AnalysisAgent()
        self.evaluation_agent = EvaluationAgent()
        self.eda_agent = EDAAgent()
        self.llm_client = MultiProviderLLM()
    
    def suggest_business_niches(self, location: str) -> List[BusinessSuggestion]:
        """Suggest business niches based on location analysis"""
        print(f"💡 Analyzing business opportunities in {location}")
        
        prompt = f"""
        Analyze the business opportunities in {location} and suggest 5 most promising business niches.
        Consider:
        - Local economy, demographics, and development
        - Existing market gaps and opportunities  
        - Growth potential and sustainability
        - Competition level and market saturation
        - Investment requirements and ROI potential
        
        Provide your analysis in structured JSON format with these fields for each suggestion:
        - business_niche: specific business type
        - reason: why suitable for this location
        - market_opportunity: specific market gap
        - investment_range: estimated investment needed
        - growth_potential: high/medium/low
        
        Focus on realistic, profitable business ideas for {location}.
        """
        
        try:
            response = self.llm_client.generate_completion(
                messages=[{"role": "user", "content": prompt}],
                model_key="gpt_oss_120b",
                max_tokens=2000
            )
            
            # Parse JSON response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            else:
                json_str = response.strip()
            
            suggestions_data = json.loads(json_str)
            
            # Convert to BusinessSuggestion objects
            suggestions = []
            for item in suggestions_data if isinstance(suggestions_data, list) else [suggestions_data]:
                suggestions.append(BusinessSuggestion(**item))
            
            return suggestions[:5]  # Return max 5 suggestions
            
        except Exception as e:
            print(f"⚠️ Business suggestion failed: {e}")
            # Return fallback suggestions
            return self._get_fallback_suggestions(location)
    
    def _get_fallback_suggestions(self, location: str) -> List[BusinessSuggestion]:
        """Provide fallback business suggestions"""
        return [
            BusinessSuggestion(
                business_niche="Food & Beverage",
                reason=f"Growing urban population in {location} with increasing dining-out culture",
                market_opportunity="Limited quality dining options with modern amenities",
                investment_range="₹10-25 lakhs",
                growth_potential="High"
            ),
            BusinessSuggestion(
                business_niche="Professional Services",
                reason=f"Developing business ecosystem in {location} needs support services",
                market_opportunity="Gap in quality professional consulting services",
                investment_range="₹5-15 lakhs", 
                growth_potential="Medium"
            )
        ]
    
    def get_scraped_data_summary(self, business_type: str, location: str) -> ScrapedDataSummary:
        """Get structured summary of scraped market data"""
        print(f"🔍 Collecting market data for {business_type} in {location}")
        
        try:
            # Get research data
            research_result = self.research_agent.conduct_research(business_type, location)
            research_data = research_result.data
            
            # Extract insights from EDA agent
            eda_data, business_insights = self.eda_agent.perform_comprehensive_eda(
                research_data, business_type, location
            )
            
            # Calculate metrics
            places_data = research_data.get("market_analysis", {}).get("places_data", [])
            total_businesses = len(places_data)
            
            # Calculate average rating
            ratings = [place.get('rating', 0) for place in places_data if place.get('rating')]
            avg_rating = sum(ratings) / len(ratings) if ratings else 0
            
            # Assess market saturation
            if total_businesses > 20:
                saturation = "High"
            elif total_businesses > 10:
                saturation = "Medium"
            else:
                saturation = "Low"
            
            # Extract top competitors
            competitors = research_data.get("market_analysis", {}).get("competitive_analysis", {}).get("top_competitors", [])
            top_competitors = [comp.get('name', 'Unknown') for comp in competitors[:3]] if competitors else ["Data not available"]
            
            # Assess data quality
            data_quality = "High" if research_result.confidence > 0.7 else "Medium"
            
            return ScrapedDataSummary(
                total_businesses=total_businesses,
                average_rating=round(avg_rating, 2),
                market_saturation=saturation,
                top_competitors=top_competitors,
                data_quality=data_quality
            )
            
        except Exception as e:
            print(f"⚠️ Data collection failed: {e}")
            return ScrapedDataSummary(
                total_businesses=0,
                average_rating=0.0,
                market_saturation="Unknown",
                top_competitors=["Data unavailable"],
                data_quality="Low"
            )
    
    def generate_business_insights(self, business_type: str, location: str) -> BusinessInsights:
        """Generate structured business insights using all agents"""
        print(f"🎯 Generating insights for {business_type} in {location}")
        
        try:
            # Get comprehensive data
            research_result = self.research_agent.conduct_research(business_type, location)
            eda_data, eda_insights = self.eda_agent.perform_comprehensive_eda(
                research_result.data, business_type, location
            )
            analysis_result = self.analysis_agent.analyze_market(
                business_type, location, research_result.data
            )
            
            # Generate evaluation insights
            evaluation_result = self.evaluation_agent.evaluate_insights(
                " ".join(eda_insights),
                " ".join(analysis_result.insights),
                business_type,
                location
            )
            
            # Extract structured insights
            key_insights = eda_insights[:5] if eda_insights else ["Market shows growth potential"]
            
            opportunities = self._extract_opportunities(evaluation_result)
            risks = self._extract_risks(evaluation_result)
            recommendations = self._extract_recommendations(evaluation_result)
            
            return BusinessInsights(
                key_insights=key_insights,
                opportunities=opportunities,
                risks=risks,
                recommendations=recommendations
            )
            
        except Exception as e:
            print(f"⚠️ Insights generation failed: {e}")
            return BusinessInsights(
                key_insights=["Market analysis completed with basic insights"],
                opportunities=["Growing customer demand", "Service differentiation"],
                risks=["Market competition", "Operational challenges"],
                recommendations=["Focus on quality service", "Build strong online presence"]
            )
    
    def generate_detailed_report(self, business_type: str, location: str) -> DetailedBusinessReport:
        """Generate comprehensive business report"""
        print(f"📊 Creating detailed report for {business_type} in {location}")
        
        try:
            # Get all necessary data
            scraped_data = self.get_scraped_data_summary(business_type, location)
            insights = self.generate_business_insights(business_type, location)
            
            prompt = f"""
            Create a comprehensive business feasibility report for starting a {business_type} in {location}.
            
            MARKET DATA SUMMARY:
            - Total Businesses: {scraped_data.total_businesses}
            - Average Rating: {scraped_data.average_rating}/5
            - Market Saturation: {scraped_data.market_saturation}
            - Top Competitors: {', '.join(scraped_data.top_competitors)}
            - Data Quality: {scraped_data.data_quality}
            
            KEY INSIGHTS:
            {json.dumps(insights.dict(), indent=2)}
            
            Please provide a detailed report with the following sections:
            
            1. EXECUTIVE SUMMARY:
               - Overall feasibility assessment
               - Key opportunities and challenges
               - Recommended approach
            
            2. MARKET ANALYSIS:
               - Market size and growth potential
               - Customer demographics and behavior
               - Trends and patterns in {location}
            
            3. COMPETITIVE LANDSCAPE:
               - Major competitors analysis
               - Competitive advantages needed
               - Market positioning strategy
            
            4. FINANCIAL PROJECTIONS:
               - Estimated startup costs
               - Revenue projections
               - Break-even analysis
               - ROI expectations
            
            5. IMPLEMENTATION PLAN:
               - Step-by-step setup process
               - Timeline and milestones
               - Resource requirements
            
            6. RISK ASSESSMENT:
               - Potential risks and challenges
               - Mitigation strategies
               - Contingency plans
            
            Make the report specific to {business_type} in {location} and data-driven.
            """
            
            response = self.llm_client.generate_completion(
                messages=[{"role": "user", "content": prompt}],
                model_key="gpt_oss_120b",
                max_tokens=4000
            )
            
            # Parse the response into structured sections
            report_data = self._parse_report_response(response, business_type, location)
            
            return DetailedBusinessReport(**report_data)
            
        except Exception as e:
            print(f"⚠️ Report generation failed: {e}")
            return self._get_fallback_report(business_type, location)
    
    def _parse_report_response(self, response: str, business_type: str, location: str) -> Dict[str, str]:
        """Parse LLM response into structured report sections"""
        # Simple parsing - in production, use more sophisticated NLP
        sections = {
            "executive_summary": "",
            "market_analysis": "", 
            "competitive_landscape": "",
            "financial_projections": "",
            "implementation_plan": "",
            "risk_assessment": ""
        }
        
        current_section = None
        lines = response.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Detect section headers
            if "executive" in line.lower() or "summary" in line.lower():
                current_section = "executive_summary"
            elif "market" in line.lower() and "analysis" in line.lower():
                current_section = "market_analysis"
            elif "competitive" in line.lower() or "competition" in line.lower():
                current_section = "competitive_landscape"
            elif "financial" in line.lower() or "projection" in line.lower():
                current_section = "financial_projections"
            elif "implementation" in line.lower() or "plan" in line.lower():
                current_section = "implementation_plan"
            elif "risk" in line.lower() or "assessment" in line.lower():
                current_section = "risk_assessment"
            elif current_section and line and not line.startswith('#'):
                sections[current_section] += line + " "
        
        # If parsing failed, create basic structure
        if not any(sections.values()):
            sections = {
                "executive_summary": f"Comprehensive analysis of {business_type} business potential in {location}.",
                "market_analysis": f"Market analysis for {business_type} in {location} based on current data.",
                "competitive_landscape": f"Competitive environment analysis for {business_type} in {location}.",
                "financial_projections": f"Financial projections and investment analysis for {business_type}.",
                "implementation_plan": f"Step-by-step implementation plan for starting {business_type} in {location}.",
                "risk_assessment": f"Risk assessment and mitigation strategies for {business_type} business."
            }
        
        return sections
    
    def _get_fallback_report(self, business_type: str, location: str) -> DetailedBusinessReport:
        """Provide fallback business report"""
        return DetailedBusinessReport(
            executive_summary=f"Analysis shows promising opportunities for {business_type} in {location} with moderate competition and good growth potential.",
            market_analysis=f"The {location} market for {business_type} shows steady growth with increasing customer demand and evolving preferences.",
            competitive_landscape=f"Moderate competition exists with opportunities for differentiation through quality service and customer experience.",
            financial_projections=f"Initial investment of ₹10-20 lakhs with break-even expected in 12-18 months and good ROI potential.",
            implementation_plan=f"1. Market research 2. Location finalization 3. Business registration 4. Setup operations 5. Marketing launch 6. Customer acquisition",
            risk_assessment=f"Key risks include competition intensity, market volatility, and operational challenges. Mitigation through quality focus and customer retention."
        )
    
    def _extract_opportunities(self, evaluation_result: Dict) -> List[str]:
        """Extract opportunities from evaluation results"""
        eval_text = evaluation_result.get("evaluation", "").lower()
        opportunities = []
        
        if "opportunity" in eval_text or "gap" in eval_text:
            opportunities.extend([
                "Market gap in premium services",
                "Digital transformation opportunity",
                "Untapped customer segments"
            ])
        
        return opportunities or ["Growing customer demand", "Service innovation potential"]
    
    def _extract_risks(self, evaluation_result: Dict) -> List[str]:
        """Extract risks from evaluation results"""
        eval_text = evaluation_result.get("evaluation", "").lower()
        risks = []
        
        if "competition" in eval_text:
            risks.append("High competition intensity")
        if "saturation" in eval_text:
            risks.append("Market saturation concerns")
        if "risk" in eval_text:
            risks.append("Market volatility risks")
            
        return risks or ["Competition pressure", "Operational challenges", "Market changes"]
    
    def _extract_recommendations(self, evaluation_result: Dict) -> List[str]:
        """Extract recommendations from evaluation results"""
        eval_text = evaluation_result.get("evaluation", "")
        recommendations = []
        
        # Simple keyword-based extraction
        lines = eval_text.split('.')
        for line in lines:
            line = line.strip().lower()
            if any(word in line for word in ['recommend', 'suggest', 'should', 'advise']):
                recommendations.append(line.capitalize())
        
        return recommendations[:3] or [
            "Focus on quality differentiation",
            "Implement digital marketing strategy",
            "Build strong customer relationships"
        ]