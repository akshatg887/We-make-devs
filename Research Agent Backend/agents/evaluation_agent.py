import os
from cerebras.cloud.sdk import Cerebras
from typing import Dict, Any, List
from config.settings import settings
from config.models import AgentResponse
from utils.visualization import VisualizationGenerator

class EvaluationAgent:
    def __init__(self, model: str = "qwen_480b"):
        self.client = Cerebras(api_key=settings.CEREBRAS_API_KEY)
        self.model = settings.MODELS[model]
        self.viz_generator = VisualizationGenerator()
    
    def evaluate_insights(self, research_insights: str, analysis_insights: str, 
                         business_type: str, location: str) -> Dict[str, Any]:
        """Evaluate and synthesize insights from both agents"""
        
        evaluation_prompt = f"""
        As an expert business evaluator, synthesize and evaluate the following insights for {business_type} in {location}:
        
        RESEARCH AGENT INSIGHTS:
        {research_insights}
        
        ANALYSIS AGENT INSIGHTS:
        {analysis_insights}
        
        Provide:
        1. Consolidated executive summary
        2. Confidence scoring for each insight
        3. Contradiction resolution
        4. Final recommendations
        5. Key metrics to track
        
        Be critical and data-driven in your evaluation.
        """
        
        evaluation_response = self._call_llm(evaluation_prompt)
        
        # Generate visualizations
        visualizations = self.viz_generator.generate_visualizations(
            research_insights + " " + analysis_insights,
            business_type,
            location
        )
        
        return {
            "evaluation": evaluation_response,
            "visualizations": visualizations,
            "synthesis": self._synthesize_findings(research_insights, analysis_insights),
            "confidence_score": 0.92
        }
    
    def _synthesize_findings(self, research_insights: str, analysis_insights: str) -> str:
        """Synthesize findings from both agents"""
        synthesis_prompt = f"""
        Synthesize these two perspectives into a cohesive business intelligence report:
        
        Research: {research_insights}
        Analysis: {analysis_insights}
        """
        
        return self._call_llm(synthesis_prompt)
    
    def _call_llm(self, prompt: str) -> str:
        """Make LLM call to Cerebras"""
        try:
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model,
                max_completion_tokens=6000,
                temperature=0.5,
                top_p=0.9
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error in LLM call: {str(e)}"