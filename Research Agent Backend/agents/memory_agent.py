# memory_agent.py
import json
from typing import Dict, Any, List
from datetime import datetime
from config.settings import settings
from tools.llm_client import MultiProviderLLM
from memory.memory_manager import BusinessMemoryManager

class MemoryEnhancedAgent:
    def __init__(self):
        self.llm_client = MultiProviderLLM()
        self.memory_manager = BusinessMemoryManager()
    
    def process_chat_with_memory(self, user_id: str, message: str, business_type: str = "", location: str = "") -> Dict[str, Any]:
        """Process user chat with comprehensive memory context"""
        
        try:
            # Get comprehensive context including research data
            context_summary = self.memory_manager.get_context_summary(user_id, business_type, location)
            
            # Create enhanced system prompt
            system_prompt = f"""
            You are an expert business intelligence analyst with access to the user's complete research history.

            {context_summary}

            CURRENT QUERY:
            User: {message}
            Business Type: {business_type if business_type else 'Not specified'}
            Location: {location if location else 'Not specified'}

            Guidelines:
            1. Use ALL available context - research data, city opportunities, scraped data, and conversation history
            2. Reference specific previous analyses when relevant
            3. Provide data-driven insights based on stored research
            4. If research data exists, use actual numbers and metrics from it
            5. Maintain conversation continuity
            6. Be specific and actionable

            If no relevant research data exists, provide general insights and suggest running comprehensive research.
            """
            
            # Generate response using LLM
            response_text = self.llm_client.generate_completion(
                messages=[{"role": "user", "content": system_prompt}],
                model_key="gpt_oss_120b",
                max_tokens=2000,
                temperature=0.7
            )
            
            # Add conversation to memory
            self.memory_manager.add_conversation(
                user_id=user_id,
                user_message=message,
                assistant_response=response_text,
                business_type=business_type,
                location=location
            )
            
            return {
                "response": response_text,
                "user_id": user_id,
                "business_type": business_type,
                "location": location,
                "timestamp": datetime.now().isoformat(),
                "has_research_context": bool(self.memory_manager.get_all_research_data(user_id))
            }
            
        except Exception as e:
            print(f"❌ Memory chat error: {e}")
            return {
                "response": "I apologize, but I'm having trouble accessing your research memory. Please try again.",
                "user_id": user_id,
                "business_type": business_type,
                "location": location,
                "timestamp": datetime.now().isoformat(),
                "has_research_context": False,
                "error": str(e)
            }
    
    def save_comprehensive_research(self, user_id: str, business_type: str, location: str, research_data: Dict[str, Any]):
        """Save comprehensive research results to memory"""
        try:
            research_summary = self.memory_manager.save_research_data(
                user_id=user_id,
                business_type=business_type,
                location=location,
                research_data=research_data
            )
            
            return {
                "message": "Research data saved to memory successfully",
                "user_id": user_id,
                "business_type": business_type,
                "location": location,
                "research_summary": research_summary,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error saving research data: {e}")
            return {
                "message": "Failed to save research data to memory",
                "user_id": user_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def save_city_opportunities(self, user_id: str, city: str, opportunities_data: Dict[str, Any]):
        """Save city opportunities to memory"""
        try:
            opportunities_summary = self.memory_manager.save_city_opportunities(
                user_id=user_id,
                city=city,
                opportunities_data=opportunities_data
            )
            
            return {
                "message": "City opportunities saved to memory successfully",
                "user_id": user_id,
                "city": city,
                "opportunities_summary": opportunities_summary,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error saving city opportunities: {e}")
            return {
                "message": "Failed to save city opportunities to memory",
                "user_id": user_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def save_scraped_data(self, user_id: str, business_type: str, location: str, scraped_data: Dict[str, Any]):
        """Save scraped data to memory"""
        try:
            scraped_summary = self.memory_manager.save_scraped_data(
                user_id=user_id,
                business_type=business_type,
                location=location,
                scraped_data=scraped_data
            )
            
            return {
                "message": "Scraped data saved to memory successfully",
                "user_id": user_id,
                "business_type": business_type,
                "location": location,
                "scraped_summary": scraped_summary,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error saving scraped data: {e}")
            return {
                "message": "Failed to save scraped data to memory",
                "user_id": user_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_conversation_history(self, user_id: str) -> Dict[str, Any]:
        """Get user's complete conversation history and research data"""
        try:
            memory_data = self.memory_manager.load_user_memory(user_id)
            
            return {
                "user_id": user_id,
                "conversation_history": memory_data.get('conversation_history', []),
                "research_data": memory_data.get('research_data', {}),
                "city_opportunities": memory_data.get('city_opportunities', {}),
                "scraped_data": memory_data.get('scraped_data', {}),
                "total_conversations": len(memory_data.get('conversation_history', [])),
                "total_research_analyses": len(memory_data.get('research_data', {})),
                "last_updated": memory_data.get('updated_at', datetime.now().isoformat())
            }
            
        except Exception as e:
            print(f"❌ Failed to get conversation history: {e}")
            return {
                "user_id": user_id,
                "conversation_history": [],
                "research_data": {},
                "city_opportunities": {},
                "scraped_data": {},
                "total_conversations": 0,
                "total_research_analyses": 0,
                "error": str(e)
            }
    
    def clear_conversation_history(self, user_id: str):
        """Clear user's complete memory"""
        self.memory_manager.clear_user_memory(user_id)
        return {
            "message": "All conversation history and research data cleared successfully",
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        }