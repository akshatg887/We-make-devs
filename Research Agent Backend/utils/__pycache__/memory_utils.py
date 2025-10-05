# memory_utils.py
import os
import json
from typing import Dict, Any, List
from datetime import datetime

class MemoryUtils:
    @staticmethod
    def calculate_memory_usage(storage_path: str = "memory_storage") -> Dict[str, Any]:
        """Calculate memory storage usage"""
        total_size = 0
        file_count = 0
        user_files = 0
        business_files = 0
        
        if os.path.exists(storage_path):
            for filename in os.listdir(storage_path):
                filepath = os.path.join(storage_path, filename)
                if os.path.isfile(filepath):
                    file_size = os.path.getsize(filepath)
                    total_size += file_size
                    file_count += 1
                    
                    if filename.startswith('user_'):
                        user_files += 1
                    elif filename.startswith('business_'):
                        business_files += 1
        
        return {
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "file_count": file_count,
            "user_memory_files": user_files,
            "business_context_files": business_files,
            "average_file_size_kb": round(total_size / max(file_count, 1) / 1024, 2),
            "last_calculated": datetime.now().isoformat()
        }
    
    @staticmethod
    def cleanup_old_memory(storage_path: str = "memory_storage", days_old: int = 30):
        """Clean up memory files older than specified days"""
        cutoff_time = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
        removed_count = 0
        
        if os.path.exists(storage_path):
            for filename in os.listdir(storage_path):
                filepath = os.path.join(storage_path, filename)
                if os.path.isfile(filepath):
                    file_time = os.path.getmtime(filepath)
                    if file_time < cutoff_time:
                        os.remove(filepath)
                        removed_count += 1
                        print(f"🧹 Removed old memory file: {filename}")
        
        return {
            "removed_files": removed_count,
            "cutoff_days": days_old,
            "cleanup_time": datetime.now().isoformat()
        }
    
    @staticmethod
    def export_memory(user_id: str, storage_path: str = "memory_storage") -> Dict[str, Any]:
        """Export user memory data"""
        from memory.memory_manager import BusinessMemoryManager
        
        memory_manager = BusinessMemoryManager(storage_path)
        
        # Load user memory
        conversation_history = memory_manager.get_conversation_history(user_id)
        
        # Find related business contexts
        business_contexts = []
        for filename in os.listdir(storage_path):
            if filename.startswith('business_'):
                filepath = os.path.join(storage_path, filename)
                try:
                    with open(filepath, 'r') as f:
                        context_data = json.load(f)
                    business_contexts.append(context_data)
                except:
                    continue
        
        return {
            "user_id": user_id,
            "export_timestamp": datetime.now().isoformat(),
            "conversation_history": conversation_history,
            "business_contexts": business_contexts,
            "total_conversations": len(conversation_history),
            "total_business_contexts": len(business_contexts)
        }