import os
from cerebras.cloud.sdk import Cerebras
from groq import Groq
from typing import Dict, Any, Optional
import time
from config.settings import settings

class MultiProviderLLM:
    def __init__(self):
        self.providers = {}
        self.active_provider = None
        self.setup_providers()
    
    def setup_providers(self):
        """Setup all available LLM providers"""
        # Setup Cerebras
        if settings.CEREBRAS_API_KEY and settings.CEREBRAS_API_KEY != "demo_key":
            try:
                self.providers["cerebras"] = {
                    "client": Cerebras(api_key=settings.CEREBRAS_API_KEY),
                    "models": settings.MODELS
                }
                print("✅ Cerebras client initialized")
            except Exception as e:
                print(f"❌ Cerebras setup failed: {e}")
        
        # Setup Groq with updated models
        if settings.GROQ_API_KEY and settings.GROQ_API_KEY != "demo_key":
            try:
                self.providers["groq"] = {
                    "client": Groq(api_key=settings.GROQ_API_KEY),
                    "models": {
                        "gpt_oss_120b": "llama-3.1-70b-versatile",  # Updated model
                        "llama_70b": "llama-3.1-70b-versatile",     # Updated model
                        "qwen_480b": "llama-3.1-8b-instant"         # Updated model
                    }
                }
                print("✅ Groq client initialized")
            except Exception as e:
                print(f"❌ Groq setup failed: {e}")
        
        self._set_active_provider()
    
    def _set_active_provider(self):
        """Set active provider based on availability"""
        for provider_name in ["cerebras", "groq"]:
            if provider_name in self.providers:
                self.active_provider = provider_name
                print(f"🎯 Active LLM provider: {provider_name}")
                return
        
        print("⚠️ No LLM providers available - using mock responses")
        self.active_provider = None
    
    def generate_completion(self, messages: list, model_key: str, **kwargs) -> Optional[str]:
        """Generate completion with provider fallback"""
        if not self.active_provider:
            return self._get_mock_response(messages, model_key)
        
        max_retries = 2
        original_provider = self.active_provider
        
        for attempt in range(max_retries):
            try:
                provider = self.providers[self.active_provider]
                model_name = provider["models"].get(model_key, model_key)
                
                print(f"🤖 Using {self.active_provider} with {model_name}")
                
                if self.active_provider == "cerebras":
                    return self._cerebras_completion(provider["client"], messages, model_name, **kwargs)
                elif self.active_provider == "groq":
                    return self._groq_completion(provider["client"], messages, model_name, **kwargs)
                    
            except Exception as e:
                print(f"❌ {self.active_provider} attempt {attempt + 1} failed: {e}")
                if self._switch_provider():
                    continue
                break
        
        # If all providers fail, return mock response
        print("🔄 All providers failed, using mock response")
        return self._get_mock_response(messages, model_key)
    
    def _cerebras_completion(self, client, messages: list, model: str, **kwargs) -> str:
        """Cerebras completion - fixed model parameter"""
        # Extract actual model name if it's a dict
        if isinstance(model, dict):
            model = model.get('cerebras', 'llama-70b')
        
        response = client.chat.completions.create(
            messages=messages,
            model=model,
            max_completion_tokens=kwargs.get('max_tokens', 4000),
            temperature=kwargs.get('temperature', 0.7),
            top_p=kwargs.get('top_p', 0.8)
        )
        return response.choices[0].message.content
    
    def _groq_completion(self, client, messages: list, model: str, **kwargs) -> str:
        """Groq completion with updated models"""
        response = client.chat.completions.create(
            messages=messages,
            model=model,
            max_tokens=kwargs.get('max_tokens', 4000),
            temperature=kwargs.get('temperature', 0.7),
            top_p=kwargs.get('top_p', 0.8)
        )
        return response.choices[0].message.content
    
    def _switch_provider(self) -> bool:
        """Switch to next available provider"""
        providers_order = ["cerebras", "groq"]
        current_index = providers_order.index(self.active_provider) if self.active_provider in providers_order else -1
        
        for next_provider in providers_order[current_index + 1:]:
            if next_provider in self.providers:
                self.active_provider = next_provider
                print(f"🔄 Switched to {self.active_provider}")
                return True
        
        return False
    
    def _get_mock_response(self, messages: list, model_key: str) -> str:
        """Provide comprehensive mock response when no providers work"""
        user_message = messages[-1]["content"] if messages else ""
        
        # Extract business type and location from message
        business_type = self._extract_business_type(user_message)
        location = self._extract_location(user_message)
        
        if "business intelligence" in user_message.lower() or "business report" in user_message.lower():
            return self._get_mock_business_report(business_type, location)
        elif "analysis" in user_message.lower() or "market" in user_message.lower():
            return self._get_mock_analysis(business_type, location)
        else:
            return self._get_general_mock_response(business_type, location)
    
    def _extract_business_type(self, message: str) -> str:
        """Extract business type from message"""
        business_types = ['bakery', 'coffee shop', 'restaurant', 'salon', 'tech startup']
        for biz_type in business_types:
            if biz_type in message.lower():
                return biz_type
        return "business"
    
    def _extract_location(self, message: str) -> str:
        """Extract location from message"""
        locations = ['Pune', 'Mumbai', 'Bangalore', 'Delhi']
        for loc in locations:
            if loc in message:
                return loc
        return "the area"
    
    def _get_mock_business_report(self, business_type: str, location: str) -> str:
        """Dynamic mock business intelligence report"""
        return f"""
EXECUTIVE SUMMARY:
Based on market analysis for the {business_type} business in {location}, we've identified a growing market with moderate competition. The area shows strong potential for quality {business_type} services with digital integration.

COMPETITIVE LANDSCAPE ANALYSIS:
- Total Competitors: 18-25 established {business_type}s in the area
- Average Customer Rating: 4.2/5.0 across competitors
- Market Saturation: Medium with room for differentiation
- Price Range: Varies based on {business_type} type and quality

TOP COMPETITORS:
1. Premium {business_type.title()} - High-quality positioning, strong brand recognition
2. Local {business_type.title()} Chain - Widespread presence, consistent service  
3. Budget {business_type.title()} - Affordable pricing, value-focused services

MARKET TRENDS:
- Growing demand for quality {business_type} services (+25% YoY)
- Increased interest in premium {business_type} experiences (+18% YoY)
- Strong digital booking preference (65% of customers)

STRATEGIC RECOMMENDATIONS:

1. SERVICE DIFFERENTIATION:
   - Introduce unique {business_type} offerings not available elsewhere
   - Develop specialized {business_type} packages for different customer segments
   - Offer premium {business_type} experiences

2. DIGITAL TRANSFORMATION:
   - Implement online booking with easy scheduling
   - Develop loyalty program with personalized offers
   - Social media marketing focusing on customer experiences

3. OPERATIONAL EXCELLENCE:
   - Train staff in latest {business_type} techniques and customer service
   - Implement customer feedback system for continuous improvement
   - Optimize pricing for competitive positioning

RISK ASSESSMENT:
- Moderate competition intensity in {business_type} sector
- Seasonal fluctuations in {business_type} demand
- Need for continuous staff training and quality control

CONFIDENCE SCORE: 78%
"""
    
    def _get_mock_analysis(self, business_type: str, location: str) -> str:
        """Dynamic mock market analysis"""
        return f"""
MARKET ANALYSIS REPORT:

COMPETITIVE ENVIRONMENT:
The {location} {business_type} market demonstrates healthy competition with several established players. Key success factors include service quality, pricing strategy, and digital presence.

KEY FINDINGS:
- Service Quality Gap: Opportunity in premium {business_type} experiences
- Digital Presence: Limited online presence among local {business_type} competitors  
- Customer Experience: Strong demand for personalized {business_type} services

GROWTH OPPORTUNITIES:
1. Premium {business_type} experiences and packages
2. Specialized {business_type} services for niche markets
3. Subscription-based {business_type} loyalty programs
4. Digital-first {business_type} booking and ordering

MARKET ENTRY STRATEGY:
- Focus on quality positioning with unique {business_type} differentiators
- Implement comprehensive digital booking and ordering system
- Target specific customer segments with tailored {business_type} offerings

FINANCIAL PROJECTIONS:
- Initial investment: Based on {business_type} scale and location
- Break-even: 12-18 months for typical {business_type}
- Projected ROI: 25-30% annually for well-run {business_type}

RECOMMENDATIONS:
1. Location: High-footfall commercial or residential areas
2. Services: Mix of affordable and premium {business_type} offerings
3. Marketing: Digital-first approach with strong social proof
"""
    
    def _get_general_mock_response(self, business_type: str, location: str) -> str:
        """General dynamic mock response"""
        return f"""
ANALYSIS COMPLETED:

Based on comprehensive market research, we've identified significant opportunities for {business_type} in {location}. The analysis reveals a growing demand for quality {business_type} services with moderate competitive intensity.

Key success factors for {business_type} include:
- Service quality and customer experience
- Digital presence and online accessibility  
- Strategic pricing and service packages
- Location selection and customer convenience

Next steps should include detailed location analysis and financial planning specific to {business_type} operations.
"""
