import os
from cerebras.cloud.sdk import Cerebras
from typing import Dict, Any
from config.settings import settings
from config.models import AgentResponse

class AnalysisAgent:
    def __init__(self, model: str = "gpt_oss_120b"):
        self.client = Cerebras(api_key=settings.CEREBRAS_API_KEY)
        self.model = settings.MODELS[model]
    
    def analyze_market(self, business_type: str, location: str, research_data: Dict[str, Any]) -> AgentResponse:
        """Analyze market conditions and competition"""
        
        analysis_prompt = f"""
        As a market analysis expert, analyze the following data for {business_type} business in {location}:
        
        Research Data: {research_data}
        
        Provide detailed analysis on:
        1. Market saturation level
        2. Competitive landscape
        3. Potential opportunities
        4. Risk factors
        5. Strategic recommendations
        
        Be data-driven and specific in your analysis.
        """
        
        analysis_response = self._call_llm(analysis_prompt)
        
        return AgentResponse(
            reasoning="Comprehensive market analysis based on scraped data",
            data=research_data,
            insights=[analysis_response],
            confidence=0.88
        )
    
    def _call_llm(self, prompt: str) -> str:
        """Make LLM call to Cerebras"""
        try:
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model,
                max_completion_tokens=5000,
                temperature=0.6,
                top_p=0.8
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error in LLM call: {str(e)}"