# models.py - Updated with structured models
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class BusinessResearchRequest(BaseModel):
    business_type: str = Field(..., description="Type of business to research")
    location: str = Field(..., description="Location for the research")
    depth: str = Field("comprehensive", description="Research depth level")

class ResearchData(BaseModel):
    raw_data: Dict[str, Any] = Field(default_factory=dict)
    insights: List[str] = Field(default_factory=list)
    metrics: Dict[str, Any] = Field(default_factory=dict)
    sources: List[str] = Field(default_factory=list)

class AgentResponse(BaseModel):
    reasoning: str = Field(default="Analysis in progress...")
    data: Optional[Dict[str, Any]] = Field(default_factory=dict)
    insights: List[str] = Field(default_factory=list)
    confidence: float = Field(default=0.0)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

# Structured output models for LLM responses
class CompetitorAnalysis(BaseModel):
    name: str = Field(..., description="Competitor business name")
    address: str = Field(..., description="Business address")
    rating: float = Field(..., description="Customer rating")
    reviews: int = Field(..., description="Number of reviews")
    price_level: str = Field(..., description="Price level category")
    strengths: List[str] = Field(..., description="Competitor strengths")
    weaknesses: List[str] = Field(..., description="Competitor weaknesses")

class MarketTrends(BaseModel):
    trend_summary: str = Field(..., description="Overall trend summary")
    average_interest: float = Field(..., description="Average interest score")
    growth_momentum: str = Field(..., description="Growth momentum indicator")
    seasonal_patterns: str = Field(..., description="Seasonal patterns identified")

class BusinessOpportunity(BaseModel):
    opportunity_type: str = Field(..., description="Type of opportunity")
    description: str = Field(..., description="Detailed opportunity description")
    potential_impact: str = Field(..., description="Potential business impact")
    implementation: str = Field(..., description="How to implement")

class MarketInsights(BaseModel):
    market_saturation: str = Field(..., description="Market saturation level")
    competitive_intensity: str = Field(..., description="Competitive intensity")
    customer_demand: str = Field(..., description="Customer demand level")
    growth_potential: str = Field(..., description="Growth potential assessment")

class StructuredResearchResponse(BaseModel):
    business_type: str = Field(..., description="Business type analyzed")
    location: str = Field(..., description="Location analyzed")
    executive_summary: str = Field(..., description="Executive summary")
    competitors: List[CompetitorAnalysis] = Field(..., description="Competitor analysis")
    market_trends: MarketTrends = Field(..., description="Market trends analysis")
    opportunities: List[BusinessOpportunity] = Field(..., description="Business opportunities")
    insights: MarketInsights = Field(..., description="Market insights")
    recommendations: List[str] = Field(..., description="Strategic recommendations")
    confidence_score: float = Field(..., description="Analysis confidence score")
    timestamp: str = Field(..., description="Analysis timestamp")
    
class BusinessSuggestion(BaseModel):
    business_type: str = Field(..., description="Type of business suggested")
    viability_score: float = Field(..., description="Viability score 0-100")
    investment_range: str = Field(..., description="Estimated investment range")
    competition_level: str = Field(..., description="Competition intensity")
    growth_potential: str = Field(..., description="Growth potential assessment")
    key_opportunities: List[str] = Field(..., description="Key opportunities")
    challenges: List[str] = Field(..., description="Potential challenges")

class CityBusinessReport(BaseModel):
    city: str = Field(..., description="City analyzed")
    population_tier: str = Field(..., description="City size category")
    economic_indicators: Dict[str, Any] = Field(..., description="Economic metrics")
    top_business_suggestions: List[BusinessSuggestion] = Field(..., description="Business recommendations")
    market_trends: List[str] = Field(..., description="Current market trends")
    consumer_behavior: Dict[str, Any] = Field(..., description="Consumer insights")
    timestamp: str = Field(..., description="Report generation timestamp")

class ComprehensiveBusinessAnalysis(BaseModel):
    business_type: str = Field(..., description="Business type analyzed")
    location: str = Field(..., description="Location analyzed")
    executive_summary: str = Field(..., description="Executive summary")
    market_overview: Dict[str, Any] = Field(..., description="Market overview")
    operational_requirements: Dict[str, Any] = Field(..., description="Operational needs")
    financial_projections: Dict[str, Any] = Field(..., description="Financial estimates")
    competitor_analysis: Dict[str, Any] = Field(..., description="Competitor insights")
    risk_assessment: Dict[str, Any] = Field(..., description="Risk analysis")
    strategic_recommendations: List[str] = Field(..., description="Strategic advice")
    real_time_data: Optional[Dict[str, Any]] = Field(..., description="Real-time market data")
    confidence_score: float = Field(..., description="Analysis confidence")
    timestamp: str = Field(..., description="Analysis timestamp")

class RealTimeMarketData(BaseModel):
    business_type: str = Field(..., description="Business type")
    location: str = Field(..., description="Location")
    data_source: str = Field(..., description="Data source")
    fresh_data: Dict[str, Any] = Field(..., description="Freshly scraped data")
    collection_time: str = Field(..., description="Data collection timestamp")
    data_quality: str = Field(..., description="Data quality assessment")