# tools/cache_manager.py - Optimized for better performance

import json
import os
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import pickle
import gzip

class CacheManager:
    def __init__(self, cache_dir: str = "cache", ttl_hours: int = 24, max_cache_size: int = 100):
        self.cache_dir = cache_dir
        self.ttl_hours = ttl_hours
        self.max_cache_size = max_cache_size
        os.makedirs(cache_dir, exist_ok=True)
        
        # Clean expired cache on initialization
        self._clean_expired_cache()
    
    def generate_cache_key(self, business_type: str, location: str, data_type: str = "research") -> str:
        """Generate a unique cache key from business type and location"""
        key_string = f"{business_type.lower()}_{location.lower()}_{data_type}"
        
        # Create MD5 hash for consistent key length
        key_hash = hashlib.md5(key_string.encode()).hexdigest()
        
        return f"{key_hash}_{data_type}"
    
    def get_cached_result(self, cache_key: str) -> Optional[Dict]:
        """Get cached result if it exists and is not expired"""
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json.gz")
        
        if not os.path.exists(cache_file):
            return None
        
        try:
            # Check if cache is expired
            file_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
            if datetime.now() - file_time > timedelta(hours=self.ttl_hours):
                os.remove(cache_file)  # Remove expired cache
                return None
            
            # Read compressed cache file
            with gzip.open(cache_file, 'rt', encoding='utf-8') as f:
                cached_data = json.load(f)
            
            # Validate cache structure
            if not self._validate_cache_data(cached_data):
                os.remove(cache_file)
                return None
            
            print(f"💾 Using cached data: {cached_data.get('cache_key', 'unknown')}")
            return cached_data.get('data')
            
        except Exception as e:
            print(f"⚠️ Cache read error: {e}")
            # Remove corrupted cache file
            try:
                os.remove(cache_file)
            except:
                pass
            return None
    
    def save_result_to_cache(self, cache_key: str, data: Dict):
        """Save result to cache with compression and metadata"""
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json.gz")
        
        # Add cache metadata
        cached_data = {
            'data': data,
            'cached_at': datetime.now().isoformat(),
            'cache_key': cache_key,
            'ttl_hours': self.ttl_hours,
            'data_size': len(str(data)),
            'version': '1.1'
        }
        
        try:
            # Use compression to save space
            with gzip.open(cache_file, 'wt', encoding='utf-8') as f:
                json.dump(cached_data, f, indent=2)
            
            print(f"💾 Cached data: {cache_key}")
            
            # Manage cache size
            self._manage_cache_size()
            
        except Exception as e:
            print(f"⚠️ Could not cache result: {e}")
    
    def clear_cache(self, specific_key: str = None):
        """Clear specific cache or all cache"""
        if specific_key:
            # Clear specific cache file
            cache_pattern = f"{specific_key}*.json.gz"
            self._clear_files_by_pattern(cache_pattern)
        else:
            # Clear all cache
            self._clear_files_by_pattern("*.json.gz")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        cache_files = [f for f in os.listdir(self.cache_dir) if f.endswith('.json.gz')]
        total_size = 0
        expired_count = 0
        valid_count = 0
        
        for cache_file in cache_files:
            file_path = os.path.join(self.cache_dir, cache_file)
            file_size = os.path.getsize(file_path)
            total_size += file_size
            
            file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            if datetime.now() - file_time > timedelta(hours=self.ttl_hours):
                expired_count += 1
            else:
                valid_count += 1
        
        return {
            "total_files": len(cache_files),
            "valid_files": valid_count,
            "expired_files": expired_count,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "cache_dir": self.cache_dir
        }
    
    def list_cached_entries(self) -> List[Dict[str, str]]:
        """List all cached entries with metadata"""
        cache_entries = []
        cache_files = [f for f in os.listdir(self.cache_dir) if f.endswith('.json.gz')]
        
        for cache_file in cache_files:
            file_path = os.path.join(self.cache_dir, cache_file)
            try:
                with gzip.open(file_path, 'rt', encoding='utf-8') as f:
                    cached_data = json.load(f)
                
                cache_entries.append({
                    'key': cached_data.get('cache_key', 'unknown'),
                    'cached_at': cached_data.get('cached_at', 'unknown'),
                    'size_kb': round(os.path.getsize(file_path) / 1024, 2),
                    'file': cache_file
                })
            except:
                continue
        
        return cache_entries
    
    def _validate_cache_data(self, cached_data: Dict) -> bool:
        """Validate cache data structure"""
        required_fields = ['data', 'cached_at', 'cache_key']
        return all(field in cached_data for field in required_fields)
    
    def _clean_expired_cache(self):
        """Clean expired cache files"""
        cache_files = [f for f in os.listdir(self.cache_dir) if f.endswith('.json.gz')]
        cleaned_count = 0
        
        for cache_file in cache_files:
            file_path = os.path.join(self.cache_dir, cache_file)
            try:
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                if datetime.now() - file_time > timedelta(hours=self.ttl_hours):
                    os.remove(file_path)
                    cleaned_count += 1
            except:
                continue
        
        if cleaned_count > 0:
            print(f"🧹 Cleaned {cleaned_count} expired cache files")
    
    def _manage_cache_size(self):
        """Manage cache size by removing oldest files if limit exceeded"""
        cache_files = []
        
        for f in os.listdir(self.cache_dir):
            if f.endswith('.json.gz'):
                file_path = os.path.join(self.cache_dir, f)
                cache_files.append((file_path, os.path.getmtime(file_path)))
        
        # Sort by modification time (oldest first)
        cache_files.sort(key=lambda x: x[1])
        
        # Remove oldest files if over limit
        while len(cache_files) > self.max_cache_size:
            oldest_file = cache_files.pop(0)
            try:
                os.remove(oldest_file[0])
                print(f"🧹 Removed old cache file: {os.path.basename(oldest_file[0])}")
            except:
                pass
    
    def _clear_files_by_pattern(self, pattern: str):
        """Clear files matching pattern"""
        import glob
        files_to_clear = glob.glob(os.path.join(self.cache_dir, pattern))
        
        for file_path in files_to_clear:
            try:
                os.remove(file_path)
                print(f"🧹 Cleared cache: {os.path.basename(file_path)}")
            except Exception as e:
                print(f"⚠️ Error clearing {file_path}: {e}")