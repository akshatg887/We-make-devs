from fastapi import FastAPI, HTTPException, Query,Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional, List
import uvicorn
from datetime import datetime
import json
from agents.research_agent import ResearchAgent
from agents.structured_analysis_agent import StructuredAnalysisAgent
from agents.business_discovery_agent import BusinessDiscoveryAgent
from agents.evaluation_agent import EvaluationAgent
from tools.searchapi_client import SearchAPIClient
from config.models import *
from agents.memory_agent import MemoryEnhancedAgent
from memory.memory_manager import BusinessMemoryManager

app = FastAPI(
    title="Market Intelligence Pro API",
    description="AI-Powered Business Discovery & Market Intelligence Platform with SearchAPI Integration",
    version="2.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agents and clients
research_agent = ResearchAgent()
analysis_agent = StructuredAnalysisAgent()
discovery_agent = BusinessDiscoveryAgent()
evaluation_agent = EvaluationAgent()
searchapi_client = SearchAPIClient()
memory_agent = MemoryEnhancedAgent()

# Helper functions (moved outside class structure)
def analyze_competitors_from_maps(maps_data: List[Dict]) -> Dict[str, Any]:
    """Analyze competitors from Google Maps data"""
    if not maps_data:
        return {}
    
    ratings = [place.get('rating', 0) for place in maps_data if place.get('rating')]
    prices = [place.get('price_level', 0) for place in maps_data if place.get('price_level')]
    reviews = [place.get('reviews', 0) for place in maps_data if place.get('reviews')]
    
    # Calculate metrics
    avg_rating = sum(ratings) / len(ratings) if ratings else 0
    avg_price = sum(prices) / len(prices) if prices else 0
    total_reviews = sum(reviews) if reviews else 0
    
    # Identify top competitors
    top_competitors = sorted(maps_data, key=lambda x: x.get('reviews', 0), reverse=True)[:5]
    
    # Analyze market gaps
    market_gaps = []
    if avg_rating < 4.0:
        market_gaps.append("Quality service gap - opportunity for high-quality offerings")
    if avg_price > 3:
        market_gaps.append("Premium market opportunity - high prices indicate willingness to pay")
    if len(maps_data) < 10:
        market_gaps.append("Low competition - market entry opportunity")
    
    return {
        'total_competitors': len(maps_data),
        'average_rating': round(avg_rating, 2),
        'average_price_level': round(avg_price, 2),
        'total_reviews': total_reviews,
        'saturation_level': 'High' if len(maps_data) > 20 else 'Medium' if len(maps_data) > 10 else 'Low',
        'top_competitors': top_competitors,
        'market_gaps': market_gaps,
        'price_analysis': {
            'budget_businesses': len([p for p in prices if p <= 2]),
            'premium_businesses': len([p for p in prices if p >= 3])
        }
    }

def analyze_trends_for_opportunities(trends_data: List[Dict], related_searches: List[Dict], business_type: str, location: str) -> Dict[str, Any]:
    """Analyze trends data to identify business opportunities"""
    if not trends_data:
        return {}
    
    # Calculate trend metrics
    values = [point.get('value', 0) for point in trends_data if point.get('value')]
    avg_interest = sum(values) / len(values) if values else 0
    
    # Identify growth trend
    if len(values) >= 2:
        growth_rate = ((values[-1] - values[0]) / values[0] * 100) if values[0] != 0 else 0
        trend_direction = 'growing' if growth_rate > 5 else 'declining' if growth_rate < -5 else 'stable'
    else:
        growth_rate = 0
        trend_direction = 'unknown'
    
    # Analyze related searches for opportunities
    opportunity_trends = []
    rising_queries = [q for q in related_searches if q.get('type') == 'rising']
    
    for query in rising_queries[:5]:
        opportunity_trends.append({
            'trend': query.get('query', ''),
            'momentum': query.get('value', 0),
            'opportunity_type': 'emerging_trend'
        })
    
    # Determine best timing based on trends
    best_timing = 'Anytime'
    if trend_direction == 'growing':
        best_timing = 'Now (growing trend)'
    elif any('seasonal' in str(q.get('query', '')).lower() for q in related_searches):
        best_timing = 'Seasonal peaks'
    
    return {
        'average_interest': round(avg_interest, 2),
        'growth_rate': round(growth_rate, 2),
        'trend_direction': trend_direction,
        'business_opportunities': opportunity_trends,
        'consumer_behavior': {
            'search_volume': 'High' if avg_interest > 70 else 'Medium' if avg_interest > 40 else 'Low',
            'trending_topics': [q.get('query') for q in rising_queries[:3]]
        },
        'best_timing': best_timing
    }

def calculate_viability_score(competitor_analysis: Dict, trend_analysis: Dict) -> float:
    """Calculate business viability score based on competition and trends"""
    base_score = 70  # Base viability score
    
    # Adjust based on competition
    competitors = competitor_analysis.get('total_competitors', 0)
    if competitors < 10:
        base_score += 15  # Low competition bonus
    elif competitors > 25:
        base_score -= 10  # High competition penalty
    
    # Adjust based on trends
    trend_direction = trend_analysis.get('trend_direction', 'unknown')
    if trend_direction == 'growing':
        base_score += 10
    elif trend_direction == 'declining':
        base_score -= 15
    
    # Adjust based on average rating (market quality)
    avg_rating = competitor_analysis.get('average_rating', 0)
    if avg_rating < 3.5:
        base_score += 10  # Opportunity for quality improvement
    
    return max(0, min(100, base_score))

def get_recommended_action(competitor_analysis: Dict, trend_analysis: Dict) -> str:
    """Get recommended action based on analysis"""
    competitors = competitor_analysis.get('total_competitors', 0)
    trend_direction = trend_analysis.get('trend_direction', 'unknown')
    
    if competitors < 5 and trend_direction == 'growing':
        return "High Opportunity - Low competition with growing market. Recommended to enter now."
    elif competitors > 20 and trend_direction == 'declining':
        return "High Risk - Saturated market with declining interest. Consider alternative business."
    elif competitors < 15 and trend_direction == 'stable':
        return "Moderate Opportunity - Stable market with room for differentiation."
    else:
        return "Evaluate Further - Mixed signals. Conduct deeper market research."

def calculate_trend_interest(trends_data: List[Dict]) -> str:
    """Calculate trend interest level"""
    if not trends_data:
        return "Unknown"
    
    values = [point.get('value', 0) for point in trends_data if point.get('value')]
    avg_value = sum(values) / len(values) if values else 0
    
    if avg_value > 70:
        return "Very High"
    elif avg_value > 50:
        return "High"
    elif avg_value > 30:
        return "Medium"
    else:
        return "Low"

def identify_market_gaps(maps_data: List[Dict], business_type: str) -> List[str]:
    """Identify market gaps from Google Maps data"""
    gaps = []
    
    if not maps_data:
        return ["No competition - First mover advantage"]
    
    ratings = [place.get('rating', 0) for place in maps_data if place.get('rating')]
    prices = [place.get('price_level', 0) for place in maps_data if place.get('price_level')]
    
    if ratings:
        avg_rating = sum(ratings) / len(ratings)
        if avg_rating < 4.0:
            gaps.append(f"Quality gap - current average rating is {avg_rating:.1f}/5.0")
    
    if prices:
        avg_price = sum(prices) / len(prices)
        if avg_price > 3:
            gaps.append("Premium market opportunity")
        elif avg_price < 2:
            gaps.append("Affordable luxury opportunity")
    
    return gaps[:3]

def assess_consumer_demand(trends_data: List[Dict]) -> str:
    """Assess consumer demand based on trends"""
    if not trends_data:
        return "Unknown"
    
    values = [point.get('value', 0) for point in trends_data if point.get('value')]
    recent_values = values[-4:] if len(values) >= 4 else values
    
    if not recent_values:
        return "Unknown"
    
    avg_recent = sum(recent_values) / len(recent_values)
    
    if avg_recent > 75:
        return "Very High"
    elif avg_recent > 60:
        return "High"
    elif avg_recent > 40:
        return "Medium"
    else:
        return "Low"

def analyze_city_trends(city_trends: List[Dict]) -> Dict[str, Any]:
    """Analyze city-specific trends"""
    if not city_trends:
        return {"trend_level": "Unknown", "growth": "Unknown"}
    
    values = [point.get('value', 0) for point in city_trends if point.get('value')]
    
    if len(values) >= 2:
        growth = ((values[-1] - values[0]) / values[0] * 100) if values[0] != 0 else 0
        trend_level = "Growing" if growth > 5 else "Declining" if growth < -5 else "Stable"
    else:
        growth = 0
        trend_level = "Unknown"
    
    return {
        "trend_level": trend_level,
        "growth_rate": round(growth, 2),
        "average_interest": round(sum(values) / len(values), 2) if values else 0
    }

def calculate_avg_investment(opportunities: List[Dict]) -> Dict[str, Any]:
    """Calculate average investment metrics"""
    if not opportunities:
        return {"range": "₹15-30 lakhs", "category": "Medium"}
    
    investments = []
    for opp in opportunities:
        investment_range = opp.get('investment_range', '₹15-25 lakhs')
        if '15-25' in investment_range:
            investments.append(20)
        elif '20-40' in investment_range:
            investments.append(30)
        elif '25-50' in investment_range:
            investments.append(37.5)
        else:
            investments.append(25)
    
    avg_investment = sum(investments) / len(investments) if investments else 25
    
    if avg_investment > 35:
        return {"range": "₹30-50+ lakhs", "category": "High", "average": avg_investment}
    elif avg_investment > 25:
        return {"range": "₹20-40 lakhs", "category": "Medium-High", "average": avg_investment}
    else:
        return {"range": "₹15-30 lakhs", "category": "Medium", "average": avg_investment}

def identify_high_growth_sectors(opportunities: List[Dict]) -> List[Dict]:
    """Identify high-growth sectors"""
    high_growth = []
    
    for opp in opportunities:
        if opp.get('growth_potential', '').lower() == 'high' and opp.get('viability_score', 0) > 75:
            search_insights = opp.get('searchapi_insights', {})
            high_growth.append({
                "sector": opp.get('business_type', 'Unknown'),
                "viability_score": opp.get('viability_score', 0),
                "growth_potential": opp.get('growth_potential', 'Medium'),
                "consumer_demand": search_insights.get('consumer_demand', 'Unknown'),
                "trend_interest": search_insights.get('trend_interest', 'Unknown')
            })
    
    return sorted(high_growth, key=lambda x: x['viability_score'], reverse=True)[:3]

def identify_low_competition_opportunities(opportunities: List[Dict]) -> List[Dict]:
    """Identify opportunities with low competition"""
    low_competition = []
    
    for opp in opportunities:
        search_insights = opp.get('searchapi_insights', {})
        competitor_count = search_insights.get('competitor_count', 0)
        
        if competitor_count < 10 and opp.get('viability_score', 0) > 70:
            low_competition.append({
                "opportunity": opp.get('business_type', 'Unknown'),
                "competitors": competitor_count,
                "viability": opp.get('viability_score', 0),
                "reason": "Low competition with high viability"
            })
    
    return sorted(low_competition, key=lambda x: x['viability'], reverse=True)[:5]

def identify_emerging_opportunities(opportunities: List[Dict], popular_searches: List[Dict]) -> List[Dict]:
    """Identify emerging opportunities based on search trends"""
    emerging = []
    trending_terms = [search.get('query', '').lower() for search in popular_searches if search.get('type') == 'rising']
    
    for opp in opportunities:
        business_type = opp.get('business_type', '').lower()
        
        # Check if business type matches any trending terms
        matching_trends = [term for term in trending_terms if any(word in business_type for word in term.split())]
        
        if matching_trends:
            emerging.append({
                "opportunity": opp.get('business_type', 'Unknown'),
                "trending_terms": matching_trends[:2],
                "viability": opp.get('viability_score', 0),
                "category": "Trend-Aligned"
            })
    
    return sorted(emerging, key=lambda x: x['viability'], reverse=True)[:5]

@app.get("/")
async def root():
    return {
        "message": "Market Intelligence Pro API with SearchAPI Integration",
        "version": "2.1.0",
        "status": "active",
        "endpoints": [
            "GET /api/comprehensive-research - Complete business and city analysis",
            "GET /api/city-opportunities - Business opportunities for a city",
            "GET /api/raw-scraped-data - Raw scraped data from SearchAPI"
        ]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Add these enhanced endpoints to main.py

@app.get("/api/comprehensive-research")
async def comprehensive_research(
    user_id: str = Query(..., description="User ID to store research in memory"),
    business_type: str = Query(..., description="Type of business to research"),
    location: str = Query(..., description="City/location for research"),
    include_raw_data: bool = Query(False, description="Include raw scraped data in response"),
    use_cache: bool = Query(True, description="Use cached results if available")
):
    """
    Comprehensive research endpoint that stores results in user memory
    """
    try:
        # Validate and clean inputs
        location = location.strip() or "Pune"
        business_type = business_type.strip()
        
        if not business_type:
            raise HTTPException(status_code=400, detail="business_type is required")
        
        print(f"🚀 Starting comprehensive research for user {user_id}: {business_type} in {location}")
        
        # Step 1: Conduct advanced research with fresh data collection
        research_response: AgentResponse = research_agent.conduct_research(
            business_type=business_type,
            location=location,
            use_cache=use_cache
        )
        
        # Step 2: Generate structured analysis
        structured_analysis = analysis_agent.generate_structured_analysis(
            research_data=research_response.data,
            business_type=business_type,
            location=location
        )
        
        # Step 3: Get comprehensive business analysis
        comprehensive_analysis = discovery_agent.generate_comprehensive_analysis(
            business_type=business_type,
            city=location
        )
        
        # Step 4: Collect real-time market data
        real_time_data = discovery_agent._collect_real_time_data(business_type, location)
        
        # Step 5: Extract key metrics from research data
        research_data = research_response.data or {}
        market_analysis = research_data.get('market_analysis', {})
        competitive_analysis = market_analysis.get('competitive_analysis', {})
        trends_analysis = market_analysis.get('trends_analysis', {})
        locality_analysis = market_analysis.get('locality_analysis', {})
        eda_analysis = market_analysis.get('eda_analysis', {})
        
        # Step 6: Prepare scraped data summary
        scraped_data_summary = {
            "places_data": {
                "total_businesses": len(real_time_data.get('places_data_summary', {}).get('top_competitors', [])),
                "average_rating": real_time_data.get('places_data_summary', {}).get('avg_rating', 0),
                "price_levels": real_time_data.get('places_data_summary', {}).get('price_levels', {}),
                "data_freshness": real_time_data.get('data_freshness', 'unknown')
            },
            "trends_data": {
                "total_trend_points": real_time_data.get('trends_data_summary', {}).get('total_trend_points', 0),
                "interest_trend": real_time_data.get('trends_data_summary', {}).get('interest_trend', 'unknown'),
                "peak_interest": real_time_data.get('trends_data_summary', {}).get('peak_interest', 0)
            },
            "collection_time": real_time_data.get('collection_time', datetime.now().isoformat())
        }
        
        # Step 7: Compile comprehensive response
        comprehensive_response = {
            "metadata": {
                "user_id": user_id,
                "business_type": business_type,
                "location": location,
                "report_timestamp": datetime.now().isoformat(),
                "data_sources": ["Google Places", "Google Trends", "Market Analysis"],
                "confidence_score": research_response.confidence
            },
            
            "executive_summary": {
                "business_overview": comprehensive_analysis.executive_summary,
                "market_opportunity": structured_analysis.executive_summary,
                "key_findings": research_response.insights[:5]
            },
            
            "market_analysis": {
                "market_overview": comprehensive_analysis.market_overview,
                "competitive_landscape": {
                    "total_competitors": competitive_analysis.get('total_competitors', 0),
                    "average_rating": competitive_analysis.get('average_rating', 0),
                    "market_saturation": competitive_analysis.get('market_saturation', 'Unknown'),
                    "top_competitors": competitive_analysis.get('top_competitors', [])[:5]
                },
                "market_trends": {
                    "trend_summary": trends_analysis.get('trend_summary', 'No data'),
                    "growth_momentum": trends_analysis.get('growth_momentum', 'unknown'),
                    "average_interest": trends_analysis.get('average_interest', 0),
                    "seasonal_patterns": trends_analysis.get('seasonal_patterns', 'No data')
                }
            },
            
            "business_metrics": {
                "operational_requirements": comprehensive_analysis.operational_requirements,
                "financial_projections": comprehensive_analysis.financial_projections,
                "risk_assessment": comprehensive_analysis.risk_assessment,
                "strategic_recommendations": comprehensive_analysis.strategic_recommendations
            },
            
            "locality_insights": {
                "business_density": locality_analysis.get('business_density', 'Unknown'),
                "customer_demand": locality_analysis.get('customer_demand', 'Unknown'),
                "growth_potential": locality_analysis.get('growth_potential', 'Unknown'),
                "opportunity_zones": locality_analysis.get('opportunity_zones', [])
            },
            
            "eda_analysis": {
                "data_quality": eda_analysis.get('data_quality', {}),
                "risk_indicators": eda_analysis.get('risk_indicators', {}),
                "opportunity_metrics": eda_analysis.get('opportunity_metrics', {}),
                "market_patterns": eda_analysis.get('market_patterns', {})
            },
            
            "scraped_data": scraped_data_summary,
            
            "visualization_data": research_data.get('visualization_data', {})
        }
        
        # Step 8: Save research data to memory
        memory_result = memory_agent.save_comprehensive_research(
            user_id=user_id,
            business_type=business_type,
            location=location,
            research_data=comprehensive_response
        )
        
        # Save scraped data separately
        memory_agent.save_scraped_data(
            user_id=user_id,
            business_type=business_type,
            location=location,
            scraped_data=scraped_data_summary
        )
        
        comprehensive_response["memory_saved"] = True
        comprehensive_response["memory_info"] = memory_result
        
        # Include raw data if requested
        if include_raw_data:
            comprehensive_response["raw_research_data"] = research_data
        
        print(f"✅ Comprehensive research completed and saved to memory for user {user_id}")
        return comprehensive_response
        
    except Exception as e:
        print(f"❌ Comprehensive research failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Comprehensive research failed: {str(e)}")

@app.get("/api/city-opportunities")
async def city_opportunities(
    user_id: str = Query(..., description="User ID to store opportunities in memory"),
    city: str = Query(..., description="City to analyze for business opportunities"),
    include_analysis: bool = Query(True, description="Include detailed analysis for top opportunities"),
    max_opportunities: int = Query(5, description="Maximum number of opportunities to return")
):
    """
    Discover and analyze business opportunities for a specific city and store in memory
    """
    try:
        # Validate and clean input
        city = city.strip() or "Pune"
        
        print(f"🎯 Discovering business opportunities for user {user_id} in {city}")
        
        # Step 1: Get city business opportunities report
        opportunities_report = discovery_agent.discover_business_opportunities(city)
        
        # Step 2: Get real-time city data
        city_data = discovery_agent._collect_city_data(city)
        
        # Step 3: Analyze top business opportunities
        top_opportunities = []
        business_analyses = []
        
        for business_suggestion in opportunities_report.top_business_suggestions[:max_opportunities]:
            try:
                if include_analysis:
                    # Get comprehensive analysis for each business type
                    analysis = discovery_agent.generate_comprehensive_analysis(
                        business_suggestion.business_type, 
                        city
                    )
                    business_analyses.append(analysis.dict())
                
                # Prepare opportunity data
                opportunity_data = {
                    "business_type": business_suggestion.business_type,
                    "viability_score": business_suggestion.viability_score,
                    "investment_range": business_suggestion.investment_range,
                    "competition_level": business_suggestion.competition_level,
                    "growth_potential": business_suggestion.growth_potential,
                    "key_opportunities": business_suggestion.key_opportunities,
                    "challenges": business_suggestion.challenges
                }
                
                top_opportunities.append(opportunity_data)
                
            except Exception as e:
                print(f"⚠️ Failed to analyze {business_suggestion.business_type}: {e}")
                continue
        
        # Step 4: Compile city ecosystem report
        city_ecosystem = {
            "city_info": {
                "name": city,
                "population_tier": opportunities_report.population_tier,
                "economic_indicators": opportunities_report.economic_indicators,
                "consumer_behavior": opportunities_report.consumer_behavior
            },
            
            "market_trends": {
                "current_trends": opportunities_report.market_trends,
                "consumer_preferences": opportunities_report.consumer_behavior.get('preferred_categories', []),
                "digital_adoption": opportunities_report.consumer_behavior.get('digital_adoption', 'Medium')
            },
            
            "business_opportunities": {
                "total_opportunities_analyzed": len(opportunities_report.top_business_suggestions),
                "top_recommendations": top_opportunities,
                "high_viability_opportunities": [
                    opp for opp in top_opportunities 
                    if opp.get('viability_score', 0) > 80
                ]
            },
            
            "investment_landscape": {
                "average_investment_range": calculate_avg_investment(top_opportunities),
                "high_growth_sectors": identify_high_growth_sectors(top_opportunities),
                "emerging_opportunities": identify_emerging_opportunities(top_opportunities)
            },
            
            "detailed_analyses": business_analyses if include_analysis else [],
            
            "report_metadata": {
                "user_id": user_id,
                "generation_timestamp": datetime.now().isoformat(),
                "opportunities_count": len(top_opportunities),
                "data_sources": ["Market Research", "Economic Indicators", "Consumer Trends"]
            }
        }
        
        # Step 5: Save to memory
        memory_result = memory_agent.save_city_opportunities(
            user_id=user_id,
            city=city,
            opportunities_data=city_ecosystem
        )
        
        city_ecosystem["memory_saved"] = True
        city_ecosystem["memory_info"] = memory_result
        
        print(f"✅ City opportunities analysis completed and saved to memory for user {user_id}")
        return city_ecosystem
        
    except Exception as e:
        print(f"❌ City opportunities analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"City opportunities analysis failed: {str(e)}")

# Keep the same persistence-chat and conversation-history endpoints from previous implementation
# They will now automatically use the enhanced memory context

@app.post("/api/persistence-chat")
async def persistence_chat(
    user_id: str = Query(..., description="Unique user identifier for memory"),
    message: str = Query(..., description="User message"),
    business_type: str = Query("", description="Business type for context"),
    location: str = Query("", description="Location for context"),
    clear_memory: bool = Query(False, description="Clear user memory before conversation")
):
    """
    Chat endpoint with persistent memory across conversations.
    Now includes comprehensive research data, city opportunities, and scraped data in context.
    """
    try:
        # Validate inputs
        if not user_id or not message:
            raise HTTPException(status_code=400, detail="user_id and message are required")
        
        # Clear memory if requested
        if clear_memory:
            result = memory_agent.clear_conversation_history(user_id)
            return JSONResponse(content=result)
        
        print(f"💬 Processing chat with full memory context for user {user_id}")
        
        # Process query with enhanced memory
        response = memory_agent.process_chat_with_memory(
            user_id=user_id,
            message=message,
            business_type=business_type,
            location=location
        )
        
        return response
        
    except Exception as e:
        print(f"❌ Persistence chat failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")

@app.get("/api/conversation-history")
async def get_conversation_history(
    user_id: str = Query(..., description="Unique user identifier")
):
    """
    Get complete conversation history and research data for a user
    """
    try:
        history_data = memory_agent.get_conversation_history(user_id)
        return history_data
        
    except Exception as e:
        print(f"❌ Failed to get conversation history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get conversation history: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )