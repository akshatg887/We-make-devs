# memory_manager.py
import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

class BusinessMemoryManager:
    def __init__(self, storage_path: str = "../memory_storage"):
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
        
    def get_user_memory_file(self, user_id: str) -> str:
        """Get file path for user memory"""
        return os.path.join(self.storage_path, f"user_{user_id}_memory.json")
    
    def get_research_data_file(self, user_id: str, business_type: str, location: str) -> str:
        """Get file path for research data"""
        key = f"{user_id}_{business_type}_{location}".lower().replace(' ', '_')
        return os.path.join(self.storage_path, f"research_{key}.json")
    
    def load_user_memory(self, user_id: str) -> Dict[str, Any]:
        """Load user conversation memory and research data"""
        memory_file = self.get_user_memory_file(user_id)
        
        if os.path.exists(memory_file):
            try:
                with open(memory_file, 'r') as f:
                    memory_data = json.load(f)
                print(f"✅ Loaded existing memory for user {user_id}")
                return memory_data
            except Exception as e:
                print(f"❌ Error loading memory for {user_id}: {e}")
        
        # Return empty memory structure
        return {
            'user_id': user_id,
            'conversation_history': [],
            'research_data': {},
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
    
    def save_user_memory(self, user_id: str, memory_data: Dict[str, Any]):
        """Save user conversation memory and research data to disk"""
        memory_file = self.get_user_memory_file(user_id)
        
        try:
            memory_data['updated_at'] = datetime.now().isoformat()
            
            with open(memory_file, 'w') as f:
                json.dump(memory_data, f, indent=2)
            
            print(f"💾 Saved memory for user {user_id}")
            
        except Exception as e:
            print(f"❌ Error saving memory for {user_id}: {e}")
    
    def save_research_data(self, user_id: str, business_type: str, location: str, research_data: Dict[str, Any]):
        """Save comprehensive research data"""
        memory_data = self.load_user_memory(user_id)
        
        # Create research key
        research_key = f"{business_type}_{location}".lower().replace(' ', '_')
        
        # Store research data summary
        research_summary = {
            'business_type': business_type,
            'location': location,
            'timestamp': datetime.now().isoformat(),
            'executive_summary': research_data.get('executive_summary', {}).get('business_overview', ''),
            'total_competitors': research_data.get('market_analysis', {}).get('competitive_landscape', {}).get('total_competitors', 0),
            'market_saturation': research_data.get('market_analysis', {}).get('competitive_landscape', {}).get('market_saturation', 'Unknown'),
            'average_rating': research_data.get('market_analysis', {}).get('competitive_landscape', {}).get('average_rating', 0),
            'investment_range': research_data.get('business_metrics', {}).get('financial_projections', {}).get('initial_investment', 'Unknown'),
            'key_opportunities': research_data.get('executive_summary', {}).get('key_findings', []),
            'scraped_data_summary': research_data.get('scraped_data', {}),
            'confidence_score': research_data.get('metadata', {}).get('confidence_score', 0)
        }
        
        # Store in memory
        if 'research_data' not in memory_data:
            memory_data['research_data'] = {}
        
        memory_data['research_data'][research_key] = research_summary
        
        # Save updated memory
        self.save_user_memory(user_id, memory_data)
        
        # Also save full research data to separate file
        research_file = self.get_research_data_file(user_id, business_type, location)
        try:
            full_research_data = {
                'user_id': user_id,
                'business_type': business_type,
                'location': location,
                'timestamp': datetime.now().isoformat(),
                'full_data': research_data
            }
            with open(research_file, 'w') as f:
                json.dump(full_research_data, f, indent=2)
            print(f"💾 Saved full research data for {user_id}, {business_type} in {location}")
        except Exception as e:
            print(f"❌ Error saving full research data: {e}")
        
        return research_summary
    
    def save_city_opportunities(self, user_id: str, city: str, opportunities_data: Dict[str, Any]):
        """Save city opportunities data"""
        memory_data = self.load_user_memory(user_id)
        
        opportunities_summary = {
            'city': city,
            'timestamp': datetime.now().isoformat(),
            'total_opportunities': opportunities_data.get('business_opportunities', {}).get('total_opportunities_analyzed', 0),
            'top_recommendations': opportunities_data.get('business_opportunities', {}).get('top_recommendations', []),
            'high_viability_opportunities': opportunities_data.get('business_opportunities', {}).get('high_viability_opportunities', []),
            'market_trends': opportunities_data.get('market_trends', {}).get('current_trends', []),
            'investment_landscape': opportunities_data.get('investment_landscape', {})
        }
        
        if 'city_opportunities' not in memory_data:
            memory_data['city_opportunities'] = {}
        
        memory_data['city_opportunities'][city.lower()] = opportunities_summary
        self.save_user_memory(user_id, memory_data)
        
        return opportunities_summary
    
    def save_scraped_data(self, user_id: str, business_type: str, location: str, scraped_data: Dict[str, Any]):
        """Save scraped data summary"""
        memory_data = self.load_user_memory(user_id)
        
        scraped_summary = {
            'business_type': business_type,
            'location': location,
            'timestamp': datetime.now().isoformat(),
            'total_businesses': scraped_data.get('places_data', {}).get('total_businesses', 0),
            'average_rating': scraped_data.get('places_data', {}).get('average_rating', 0),
            'data_freshness': scraped_data.get('places_data', {}).get('data_freshness', 'unknown'),
            'total_trend_points': scraped_data.get('trends_data', {}).get('total_trend_points', 0),
            'interest_trend': scraped_data.get('trends_data', {}).get('interest_trend', 'unknown')
        }
        
        if 'scraped_data' not in memory_data:
            memory_data['scraped_data'] = {}
        
        research_key = f"{business_type}_{location}".lower().replace(' ', '_')
        memory_data['scraped_data'][research_key] = scraped_summary
        self.save_user_memory(user_id, memory_data)
        
        return scraped_summary
    
    def add_conversation(self, user_id: str, user_message: str, assistant_response: str, 
                        business_type: str = "", location: str = ""):
        """Add conversation to memory"""
        memory_data = self.load_user_memory(user_id)
        
        conversation_entry = {
            "user_message": user_message,
            "assistant_response": assistant_response,
            "business_type": business_type,
            "location": location,
            "timestamp": datetime.now().isoformat()
        }
        
        memory_data['conversation_history'].append(conversation_entry)
        
        # Keep only last 50 conversations to manage size
        if len(memory_data['conversation_history']) > 50:
            memory_data['conversation_history'] = memory_data['conversation_history'][-50:]
        
        self.save_user_memory(user_id, memory_data)
        return conversation_entry
    
    def get_research_summary(self, user_id: str, business_type: str, location: str) -> Optional[Dict[str, Any]]:
        """Get research data summary for specific business and location"""
        memory_data = self.load_user_memory(user_id)
        research_key = f"{business_type}_{location}".lower().replace(' ', '_')
        
        return memory_data.get('research_data', {}).get(research_key)
    
    def get_all_research_data(self, user_id: str) -> Dict[str, Any]:
        """Get all research data for user"""
        memory_data = self.load_user_memory(user_id)
        return memory_data.get('research_data', {})
    
    def get_context_summary(self, user_id: str, business_type: str = "", location: str = "") -> str:
        """Get comprehensive context summary for LLM"""
        memory_data = self.load_user_memory(user_id)
        
        summary = f"USER CONTEXT for {user_id}:\n\n"
        
        # Research data context
        research_data = memory_data.get('research_data', {})
        if research_data:
            summary += "PREVIOUS RESEARCH ANALYSES:\n"
            for key, research in list(research_data.items())[-3:]:  # Last 3 researches
                summary += f"- {research['business_type']} in {research['location']}:\n"
                summary += f"  Competitors: {research.get('total_competitors', 0)}\n"
                summary += f"  Market: {research.get('market_saturation', 'Unknown')}\n"
                summary += f"  Investment: {research.get('investment_range', 'Unknown')}\n"
                summary += f"  Confidence: {research.get('confidence_score', 0)}\n"
        
        # City opportunities context
        city_opportunities = memory_data.get('city_opportunities', {})
        if city_opportunities:
            summary += "\nCITY OPPORTUNITIES ANALYZED:\n"
            for city, opportunities in list(city_opportunities.items())[-2:]:  # Last 2 cities
                summary += f"- {city.title()}: {opportunities.get('total_opportunities', 0)} opportunities found\n"
        
        # Scraped data context
        scraped_data = memory_data.get('scraped_data', {})
        if scraped_data:
            summary += "\nSCRAPED DATA AVAILABLE:\n"
            for key, scraped in list(scraped_data.items())[-3:]:  # Last 3 scraped datasets
                summary += f"- {scraped['business_type']} in {scraped['location']}: {scraped.get('total_businesses', 0)} businesses\n"
        
        # Conversation history context
        conversation_history = memory_data.get('conversation_history', [])
        if conversation_history:
            summary += "\nRECENT CONVERSATION HISTORY:\n"
            for chat in conversation_history[-5:]:  # Last 5 conversations
                if chat.get('business_type') == business_type and chat.get('location') == location:
                    summary += f"User: {chat['user_message'][:100]}...\n"
                    summary += f"You: {chat['assistant_response'][:100]}...\n"
        
        if summary == f"USER CONTEXT for {user_id}:\n\n":
            summary += "No previous data available for this user.\n"
        
        return summary
    
    def clear_user_memory(self, user_id: str):
        """Clear all user memory"""
        memory_file = self.get_user_memory_file(user_id)
        if os.path.exists(memory_file):
            os.remove(memory_file)
        
        # Also remove research data files
        for filename in os.listdir(self.storage_path):
            if filename.startswith(f"research_{user_id}_"):
                os.remove(os.path.join(self.storage_path, filename))
        
        print(f"🧹 Cleared all memory for user {user_id}")